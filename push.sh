find . -name "*.pyc" -exec rm -rf {} \;
git add --all
git commit -m 'witty commit message'
git push -u origin master
