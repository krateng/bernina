from bernina import yamlparse

testfiles = [
	"testlibrary/tscc.yml",
	"testlibrary/tscc2.yml",
	"testlibrary/tscc3.yml",
]

testresults = [yamlparse.parse(f) for f in testfiles]

for f in testresults[1:]:
	assert testresults[0] == f

print("All good!")
