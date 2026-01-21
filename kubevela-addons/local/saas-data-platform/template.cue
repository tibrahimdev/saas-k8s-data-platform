package main
output: {
	apiVersion: "core.oam.dev/v1beta1"
	kind:       "Application"
	spec: {
		components: [
			{
				type: "k8s-objects"
				name: "workspace-ns"
				properties: objects: [{
					apiVersion: "v1"
					kind: "Namespace"
					metadata: name: parameter.namespace
				}]
			},
			certManager,
		]
		policies: [
			{
				type: "shared-resource"
				name: "namespace"
				properties: rules: [{
					selector: resourceTypes: ["Namespace"]
				}]
			},
			// {
			// 	name: "read-only-ns"
			// 	type: "read-only"
			// 	properties: {
			// 		rules: [
			// 			{
			// 				selector: {
			// 					resourceTypes: ["Namespace"]
			// 				}
			// 			}
			// 		]
			// 	}
			// },
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
