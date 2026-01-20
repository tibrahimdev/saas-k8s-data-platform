/*
Copyright 2026.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package platform

import (
	"context"
	"time"

	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
	"sigs.k8s.io/controller-runtime/pkg/log"

	platformv1beta1 "github.com/tibrahim/saas-operator/api/platform/v1beta1"
)

// WorkspaceReconciler reconciles a Workspace object
type WorkspaceReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

// +kubebuilder:rbac:groups=platform.tibrahim.dev,resources=workspaces,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=platform.tibrahim.dev,resources=workspaces/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=platform.tibrahim.dev,resources=workspaces/finalizers,verbs=update

// Reconcile is part of the main kubernetes reconciliation loop which aims to
// move the current state of the cluster closer to the desired state.
// TODO(user): Modify the Reconcile function to compare the state specified by
// the Workspace object against the actual cluster state, and then
// perform operations to make the cluster state reflect the state specified by
// the user.
//
// For more details, check Reconcile and its Result here:
// - https://pkg.go.dev/sigs.k8s.io/controller-runtime@v0.22.4/pkg/reconcile
func (r *WorkspaceReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := log.FromContext(ctx)
	log.Info("Reconciling workspace", "workspace", req.NamespacedName)

	ws := &platformv1beta1.Workspace{}
	workspaceFinalizer := "workspace.platform.tibrahim.dev/finalizer"

	// get
	if err := r.Get(ctx, req.NamespacedName, ws); err != nil {
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	if ws.ObjectMeta.DeletionTimestamp.IsZero() {
		// The object is not being deleted, so if it does not have our finalizer, then let's add the finalizer and update the object. This is equivalent to registering our finalizer.
		if !controllerutil.ContainsFinalizer(ws, workspaceFinalizer) {
			controllerutil.AddFinalizer(ws, workspaceFinalizer)
			if err := r.Update(ctx, ws); err != nil {
				return ctrl.Result{}, err
			}
			return ctrl.Result{}, nil
		}
	} else {
		// The object is being deleted
		if controllerutil.ContainsFinalizer(ws, workspaceFinalizer) {
			log.Info("Deleting workspace", "workspace", req.NamespacedName)
			// TODO: delete/cleanup logic
		}

		// remove finalizer from the list and update it
		controllerutil.RemoveFinalizer(ws, workspaceFinalizer)
		if err := r.Update(ctx, ws); err != nil {
			return ctrl.Result{}, err
		}
	}

	// remote, err := poll saas
	// if err:
	// 	requeue with backoff
	// 	return

	// changed := sync status
	// if changed:
	// 	update status

	// requeue after interval

	return ctrl.Result{
		RequeueAfter: 10 * time.Second,
	}, nil
}

// SetupWithManager sets up the controller with the Manager.
func (r *WorkspaceReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&platformv1beta1.Workspace{}).
		Named("platform-workspace").
		Complete(r)
}
