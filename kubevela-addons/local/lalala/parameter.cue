// parameter.cue is used to store addon parameters.
//
// You can use these parameters in template.cue or in resources/ by 'parameter.myparam'
//
// For example, you can use parameters to allow the user to customize
// container images, ports, and etc.
parameter: {
	// +usage=Custom parameter description
	namespace: *"workspace" | string
	//+usage=Cert Manager config
	certManager: {
		//+usage=Namespace to deploy to, defaults to saas-workload
		namespace: *"workspace" | string
		// +usage=Specify if install the CRDs before installing cert-manager or not
		installCRDs: *true | bool
		// +usage=Specify if upgrade the CRDs when upgrading cert-manager or not
		upgradeCRD: *false | bool
		//+usage=Number of replicas
		replicas: *1 | int
	}
	jupyterhub: {
		// +usage=Enable or disable JupyterHub
		enabled: *true | bool
		//+usage=Namespace to deploy to, defaults to saas-workload
		namespace: *"saas-workload" | string

		// postgres: {
		// 	// +usage=Name of the Postgres component (CloudNativePG)
		// 	componentName: *"jupyterhub-postgres" | string

		// 	// +usage=Database name used by JupyterHub
		// 	database: *"jupyterhub" | string
		// }
	}
}
