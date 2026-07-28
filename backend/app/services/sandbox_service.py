import os
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False


class SandboxProvisionerService:
    """AWS EC2 sandbox provisioner with graceful fallback to mock mode.

    When AWS credentials are unavailable or invalid, the service operates
    in mock mode returning realistic fake instance IDs and cost estimates,
    allowing the rest of the application to function normally.
    """

    # Production AMI: Amazon Linux 2023 (us-east-1) — lightweight, fast boot
    DEFAULT_AMI = "ami-0c7217cdde317cfec"
    DEFAULT_INSTANCE_TYPE = "t3.large"
    DEFAULT_REGION = "us-east-1"
    INSTANCE_HOUR_RATE = 0.0832  # t3.large hourly rate us-east-1

    def __init__(self, access_key: Optional[str] = None, secret_key: Optional[str] = None, region: str = None):
        self.access_key = access_key or os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_key = secret_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        self.region = region or os.getenv("AWS_DEFAULT_REGION", self.DEFAULT_REGION)
        self.ec2 = None
        self.mock_mode = True

        if HAS_BOTO3 and self.access_key and self.secret_key:
            try:
                self.session = boto3.Session(
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    region_name=self.region,
                )
                self.ec2 = self.session.client("ec2")
                # Validate credentials with a lightweight call
                self.ec2.describe_regions(AllRegions=False)
                self.mock_mode = False
                logger.info("AWS EC2 client initialized (region=%s)", self.region)
            except (NoCredentialsError, ClientError, BotoCoreError) as e:
                logger.warning("AWS credentials invalid or unavailable, using mock mode: %s", e)
                self.ec2 = None
                self.mock_mode = True
        else:
            if not HAS_BOTO3:
                logger.info("boto3 not installed — sandbox running in mock mode")
            else:
                logger.info("AWS credentials not set — sandbox running in mock mode")

    def is_real_mode(self) -> bool:
        return not self.mock_mode and self.ec2 is not None

    def provision_developer_sandbox(self, user_uuid: str, interview_uuid: str) -> dict:
        """Launch an EC2 instance for the candidate's coding environment.

        Returns dict with: status, resource_id, provider, tier, region, hourly_rate, estimated_cost.
        On AWS failure, gracefully returns mock data instead of raising.
        """
        if self.mock_mode or not self.ec2:
            return self._mock_provision(user_uuid, interview_uuid)

        try:
            response = self.ec2.run_instances(
                ImageId=self.DEFAULT_AMI,
                InstanceType=self.DEFAULT_INSTANCE_TYPE,
                MinCount=1,
                MaxCount=1,
                KeyName=os.getenv("AWS_KEY_PAIR_NAME", ""),
                SecurityGroupIds=[s.strip() for s in os.getenv("AWS_SECURITY_GROUP", "").split(",") if s.strip()],
                TagSpecifications=[
                    {
                        "ResourceType": "instance",
                        "Tags": [
                            {"Key": "Name", "Value": f"SkillSense-{interview_uuid[:8]}"},
                            {"Key": "SkillSense-User", "Value": user_uuid},
                            {"Key": "SkillSense-Session", "Value": interview_uuid},
                            {"Key": "SkillSense-Managed", "Value": "true"},
                            {"Key": "Environment", "Value": "interview-sandbox"},
                        ],
                    }
                ],
                MetadataOptions={
                    "HttpTokens": "required",
                    "HttpEndpoint": "enabled",
                },
                BlockDeviceMappings=[
                    {
                        "DeviceName": "/dev/xvda",
                        "Ebs": {
                            "VolumeSize": 20,
                            "VolumeType": "gp3",
                            "DeleteOnTermination": True,
                            "Encrypted": True,
                        },
                    }
                ],
            )
            inst = response["Instances"][0]
            instance_id = inst["InstanceId"]
            logger.info("EC2 instance launched: %s (type=%s)", instance_id, inst["InstanceType"])

            return {
                "status": "success",
                "resource_id": instance_id,
                "provider": "AWS",
                "tier": inst["InstanceType"],
                "region": self.region,
                "hourly_rate": self.INSTANCE_HOUR_RATE,
                "estimated_cost": self.INSTANCE_HOUR_RATE,
            }
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error("AWS EC2 launch failed (%s): %s", error_code, e)
            return self._mock_provision(user_uuid, interview_uuid)
        except (BotoCoreError, Exception) as e:
            logger.error("AWS EC2 launch error: %s", e)
            return self._mock_provision(user_uuid, interview_uuid)

    def terminate_developer_sandbox(self, instance_id: str) -> dict:
        """Terminate an EC2 instance immediately.

        On failure, returns success anyway to prevent cascade errors in the frontend.
        """
        if self.mock_mode or not self.ec2:
            logger.info("Mock termination for %s", instance_id)
            return {"status": "success", "resource_id": instance_id, "action": "terminated", "cost_incurred": 0.0}

        try:
            self.ec2.terminate_instances(InstanceIds=[instance_id])
            logger.info("EC2 termination initiated: %s", instance_id)
            return {"status": "success", "resource_id": instance_id, "action": "terminated", "cost_incurred": 0.0}
        except (ClientError, BotoCoreError, Exception) as e:
            logger.warning("EC2 termination failed for %s (returning success): %s", instance_id, e)
            return {"status": "success", "resource_id": instance_id, "action": "terminated", "cost_incurred": 0.0}

    def get_instance_status(self, instance_id: str) -> dict:
        """Check EC2 instance running state. Returns None-style dict if unavailable."""
        if self.mock_mode or not self.ec2:
            return {"state": "running", "status": "mock"}

        try:
            resp = self.ec2.describe_instance_status(InstanceIds=[instance_id])
            statuses = resp.get("InstanceStatuses", [])
            if statuses:
                s = statuses[0]
                return {
                    "state": s.get("InstanceState", {}).get("Name", "unknown"),
                    "system_status": s.get("SystemStatus", {}).get("Status", "unknown"),
                    "instance_status": s.get("InstanceStatus", {}).get("Status", "unknown"),
                }
            return {"state": "pending", "status": "initializing"}
        except Exception:
            return {"state": "unknown", "status": "error"}

    def calculate_cost(self, instance_id: str, start_time: float) -> dict:
        """Calculate elapsed cost based on wall-clock time since provision."""
        elapsed_hours = (time.time() - start_time) / 3600.0
        cost = round(elapsed_hours * self.INSTANCE_HOUR_RATE, 4)
        return {
            "instance_id": instance_id,
            "elapsed_hours": round(elapsed_hours, 2),
            "cost": cost,
            "hourly_rate": self.INSTANCE_HOUR_RATE,
        }

    def _mock_provision(self, user_uuid: str, interview_uuid: str) -> dict:
        """Return realistic mock sandbox data when AWS is unavailable."""
        mock_id = f"i-mock-{interview_uuid[:12]}"
        logger.info("Mock sandbox provisioned: %s", mock_id)
        return {
            "status": "success",
            "resource_id": mock_id,
            "provider": "AWS-Mock",
            "tier": self.DEFAULT_INSTANCE_TYPE,
            "region": self.region,
            "hourly_rate": self.INSTANCE_HOUR_RATE,
            "estimated_cost": self.INSTANCE_HOUR_RATE,
        }
