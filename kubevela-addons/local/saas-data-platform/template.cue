package main
output: {
	apiVersion: "core.oam.dev/v1beta1"
	kind:       "Application"
	spec: {
		components: []
		policies: [
			{
				name: "read-only-ns"
				type: "read-only"
				properties: {
					rules: [
						{
							selector: {
								resourceTypes: ["Namespace"]
							}
						}
					]
				}
			},
			// {
			// 	name: "apply-once-policy"
			// 	type: "apply-once"
			// 	properties: {
			// 		enable: true
			// 		rules: [
			// 			{
			// 				selector: {
			// 					resourceTypes: ["Namespace"]
			// 				}
			// 				strategy: {
			// 					onUpdate: "onAppUpdate"
			// 				}
			// 			}
			// 		]
			// 	}
			// }
		]
	}
}
