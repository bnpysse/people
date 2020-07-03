from requests_html import HTMLSession

login_url1 = 'https://shibb-idp.georgetown.edu/idp/profile/SAML2/POST/SSO'

login_url2 = 'https://shibb-idp.georgetown.edu/idp/profile/SAML2/POST/SSO?execution=e1s1'

data = {'j_username': 'yf170', 'j_password': 'wuzpes-xownif-3pIntu'}

s = HTMLSession()

r = s.post(login_url1, data=data)

r.html.render()

r = s.post(login_url2, data=data)

print(r.status_code)

for i in r.cookies:
    print(i)