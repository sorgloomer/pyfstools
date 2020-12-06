# update CHANGELOG.md
# bump version in pyfstools/__init__.py
# push version tag
# create github release

# pypi user is __token__

python -m pip install --upgrade pip
python -m pip install --user --upgrade setuptools wheel
python -m pip install --user --upgrade twine

rm -rf dist/
rm -rf build/
rm -rf pyfsftpserver.egg-info/
rm -f MANIFEST
python setup.py sdist bdist_wheel

if [[ "$*" == "--live" ]]
then
    python -m twine upload --verbose dist/*
else
    python -m twine upload --verbose --repository testpypi dist/*
fi
