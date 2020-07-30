import numpy as np
import matplotlib.pyplot as plt
from nilearn import plotting, datasets

from hcp_regions import HCPRegions
from parameters import *
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, train_test_split
import pickle
import os
from plotting import *

from plotting import plot_cross_validation_boxplot, plot_brain_visualization
from utils import *

ts_wm_subjs = load_subjects_timeseries()

def build_logistic_matrix(task_bold_timeseries_subjs, run, conditions):
    n_conditions = len(conditions)
    X = np.empty((N_SUBJECTS*n_conditions, N_PARCELS))
    for subj in subjects:
        for k, cond in enumerate(conditions):
            X[k*N_SUBJECTS + subj, :] = get_condition_bold(subj, 'wm', cond, run, task_bold_timeseries_subjs[subj])
    return X

# # faces vs tools
# conditions_faces_tools = ['2bk_faces', '0bk_faces', '2bk_tools', '0bk_tools']
# X_run0 = build_logistic_matrix(ts_wm_subjs, run=0, conditions=conditions_faces_tools)
# y_run0 = np.concatenate(([0]*N_SUBJECTS*2,[1]*N_SUBJECTS*2))

# faces, tools, places, body
conditions_all = ['2bk_faces', '0bk_faces', '2bk_tools', '0bk_tools', '2bk_places', '0bk_places', '2bk_body', '0bk_body']
X_run0 = build_logistic_matrix(ts_wm_subjs, run=0, conditions=conditions_all)
y_run0 = np.concatenate(([0]*N_SUBJECTS*2,[1]*N_SUBJECTS*2, [2]*N_SUBJECTS*2, [3]*N_SUBJECTS*2))

# X_run1 = np.empty((N_SUBJECTS*4, N_PARCELS))
# build_logistic_matrix(ts_wm_subjs, run=1, conditions=conditions_faces_tools)

print("Finished separating BOLD signal using the task blocks.")


X_train, X_test, y_train, y_test  = train_test_split(X_run0, y_run0, test_size=.2)

# y_run1 = np.copy(y_run0)
# X_run1_train, X_run1_test, y_run1_train, y_run1_test  = train_test_split(X_run1, y_run1)

# X = np.concatenate([X_run0_train, X_run1_train])
# y = np.concatenate([y_run0_train, y_run1_train])

# X, y = X_run0, y_run0

# X_test = np.concatenate([X_run0_test, X_run1_test])
# y_test = np.concatenate([y_run0_test, y_run1_test])

#%%
print("Start regressions.")
# # First define the model
log_reg = LogisticRegression(penalty="none")

#Then fit it to data
log_reg.fit(X_train, y_train)

coefs = np.copy(log_reg.coef_[0,:])
#%%
n_most_active = 10
most_active_regions = np.argsort(-coefs)[:n_most_active]  # get n_most_active highest coefficients
h = HCPRegions()
for region_id in most_active_regions:
    region_name = region_info['name'][region_id]
    splithemis = region_name.split("_")[0]
    splithemis = "Right" if splithemis == "R" else "Left"
    splitreg = region_name.split("_")[1]
    print((splithemis, h.get_entry(splitreg)["AreaDescription"], coefs[region_id], region_info['network'][region_id]))


acc_train = np.mean(log_reg.predict(X_train)==y_train)
print("Accuracy for training set =", acc_train)
# predictions = log_reg.predict(X)
acc_test = np.mean(log_reg.predict(X_test)==y_test)
print("Accuracy for test set =", )
plt.figure()
plt.title("Decoding accuracy: Training vs Test")
plt.bar(["Training","Test"], [acc_train*100,100*acc_test])
plt.ylabel("Accuracy (%)")

#%%

# Split across subjects
kfold=4  # k-fold cross-validation
accuracies = cross_val_score(log_reg, X_run0, y_run0, cv=kfold)
plot_cross_validation_boxplot(accuracies, kfold)

plt.show()

#%%
# # code below not working if not in a notebook
# fsaverage = datasets.fetch_surf_fsaverage()
# surf_coefs = coefs[atlas["labels_L"]]
# plotting.view_surf(fsaverage['infl_left'],
#                    surf_coefs)
#
# plotting.show()
