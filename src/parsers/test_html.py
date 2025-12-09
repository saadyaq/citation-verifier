from html_parser import parse_url

page = parse_url('https://en.wikipedia.org/wiki/Python_(programming_language)')
print(f'Title: {page.title}')
print(f'Status: {page.fetch_status}')
print(f'Text length: {len(page.text)}')
print(f'First 500 chars: {page.text[:500]}')