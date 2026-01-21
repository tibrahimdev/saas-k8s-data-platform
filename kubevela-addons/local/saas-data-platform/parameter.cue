// parameter.cue is used to store addon parameters.
//
// You can use these parameters in template.cue or in resources/ by 'parameter.myparam'
//
// For example, you can use parameters to allow the user to customize
// container images, ports, and etc.
parameter: {
	// +usage=Custom parameter description
	namespace: *"saas" | string
	//+usage=Cert Manager config
	certManager: {
		//+usage=Namespace to deploy to, defaults to saas
		namespace: *"saas" | string
		// +usage=Specify if install the CRDs before installing cert-manager or not
		installCRDs: *true | bool
		// +usage=Specify if upgrade the CRDs when upgrading cert-manager or not
		upgradeCRD: *false | bool
		//+usage=Number of replicas
		replicas: *1 | int
	}
}
