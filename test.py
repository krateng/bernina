from bernina import yamlparse
import yaml

testfiles = [
	"example_infofiles/tscc.yml",
	"example_infofiles/tscc2.yml",
	"example_infofiles/tscc3.yml",
]

testresults = [yamlparse.parse(f) for f in testfiles]

res = {}
for t in testresults:
	res.update(t)
	print(t)
#print(yaml.dump(res))
