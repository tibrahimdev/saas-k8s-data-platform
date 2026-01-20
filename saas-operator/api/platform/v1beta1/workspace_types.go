package v1beta1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// WorkspaceSpec defines the desired state of Workspace
type WorkspaceSpec struct {
	WorkspaceId            string `json:"workspaceId"`
	PlatformProviderName   string `json:"platformProviderName"`
	PlatformProviderRegion string `json:"platformProviderRegion"`
}

type WorkspacePhase string

const (
	WorkspacePending  WorkspacePhase = "PENDING"
	WorkspaceCreating WorkspacePhase = "CREATING"
	WorkspaceRunning  WorkspacePhase = "RUNNING"
	WorkspaceFailed   WorkspacePhase = "FAILED"
	WorkspaceDeleting WorkspacePhase = "DELETING"
	WorkspaceDeleted  WorkspacePhase = "DELETED"
)

// WorkspaceStatus defines the observed state of Workspace.
type WorkspaceStatus struct {
	Phase      WorkspacePhase     `json:"phase,omitempty"`
	Conditions []metav1.Condition `json:"conditions,omitempty"`
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status

// Workspace is the Schema for the workspaces API
type Workspace struct {
	metav1.TypeMeta `json:",inline"`

	// metadata is a standard object metadata
	// +optional
	metav1.ObjectMeta `json:"metadata,omitempty"`

	// spec defines the desired state of Workspace
	// +required
	Spec WorkspaceSpec `json:"spec,omitempty"`

	// status defines the observed state of Workspace
	// +optional
	Status WorkspaceStatus `json:"status,omitempty"`
}

// +kubebuilder:object:root=true

// WorkspaceList contains a list of Workspace
type WorkspaceList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []Workspace `json:"items"`
}

func init() {
	SchemeBuilder.Register(&Workspace{}, &WorkspaceList{})
}
