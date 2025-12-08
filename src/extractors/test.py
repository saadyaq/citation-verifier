from claim_extractor import extract_claims

with open("test_doc.md") as f :
    text=f.read()

claims = extract_claims(text)
for c in claims:
    print(f'Claim: {c.claim_text}')
    print(f'URL: {c.citation_url}')
    print(f'Ref: {c.citation_ref}')
    print('---')