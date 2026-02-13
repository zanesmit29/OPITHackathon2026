import sys
print('Python:', sys.version.split()[0])
print('-' * 40)

# Test imports
packages = [
    ('crewai', 'CrewAI'),
    ('langchain', 'LangChain'),
    ('transformers', 'Transformers'),
    ('sentence_transformers', 'Sentence Transformers'),
    ('faiss', 'FAISS'),
    ('pandas', 'Pandas'),
    ('numpy', 'NumPy'),
    ('pypdf', 'PyPDF'),
    ('docx', 'Python-DOCX'),
    ('bs4', 'BeautifulSoup4'),
]

for module, name in packages:
    try:
        mod = __import__(module)
        version = getattr(mod, '__version__', 'installed')
        print(f'✓ {name}: {version}')
    except ImportError as e:
        print(f'✗ {name}: FAILED')

print('-' * 40)
print('✓ Setup complete!')