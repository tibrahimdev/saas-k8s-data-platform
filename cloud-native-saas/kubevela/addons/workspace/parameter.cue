// parameter.cue is used to store addon parameters.
//
// You can use these parameters in template.cue or in resources/ by 'parameter.myparam'
//
// For example, you can use parameters to allow the user to customize
// container images, ports, and etc.
parameter: {
	// +usage=Custom parameter description
	namespace: *"saas-system" | string

	jupyterhub: {
		// +usage=Enable or disable JupyterHub
		enabled: *true | bool
		//+usage=Namespace to deploy to, defaults to saas-workload
		namespace: *"saas-workload" | string
		version:   *"4.3.2" | string

		db: {
			provider: *"kubernetes" | "cloud-managed" 
			storageSize: *"10Gi" | string

			if provider == "kubernetes" {
				cnpg: {
					instances: *1 | int
				}
			}

			if provider == "rds" {
				rds: {
					engine:        *"postgres" | "mysql"
					instanceClass: string
					region:        string
				}
			}
		}

		// postgres: {
		// 	// +usage=Name of the Postgres component (CloudNativePG)
		// 	componentName: *"jupyterhub-postgres" | string

		// 	// +usage=Database name used by JupyterHub
		// 	database: *"jupyterhub" | string
		// }
	}
}
