parameter: {
	// +usage=The clusters to install
	clusters?: [...string]
	// +usage=Specify if upgrade the CRDs when upgrading keda or not
	upgradeCRD: *false | bool
}
