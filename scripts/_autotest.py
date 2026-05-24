import http.client, json, uuid

b = uuid.uuid4().hex
lines = []
for k, v in [('interview_id','ffffffff-ffff-ffff-ffff-ffffffffffff'),
             ('question_text','What is Docker?'),
             ('transcript','Docker containers package apps.'),
             ('file','x')]:
    lines.append('--' + b)
    if k == 'file':
        lines.append('Content-Disposition: form-data; name="' + k + '"; filename="a.webm"')
        lines.append('Content-Type: audio/webm')
    else:
        lines.append('Content-Disposition: form-data; name="' + k + '"')
    lines.append('')
    lines.append(str(v))
lines.append('--' + b + '--')
body = b'\r\n'.join(l.encode() for l in lines)

c = http.client.HTTPConnection('localhost', 8000, timeout=30)
c.request('POST', '/api/v1/candidate/submit-answer', body,
          {'Content-Type': 'multipart/form-data; boundary=' + b})
r = c.getresponse()
d = json.loads(r.read())
print(f'Status: {r.status}')
if r.status == 200:
    g = d['grades']
    print(f'Tech:{g["score_tech"]} Comm:{g["score_comm"]} Rel:{g["score_rel"]}')
else:
    print(f'Error: {str(d)[:200]}')
c.close()
