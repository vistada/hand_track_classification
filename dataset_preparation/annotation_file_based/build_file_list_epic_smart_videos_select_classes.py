# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 01:26:56 2018

Make lists for mfnet activity classification based on the epic kitchens splits for videos

only select classes for debugging purposes

@author: Γιώργος
"""

import os
import pandas

get_track_class = lambda x: int(x.split('_')[1])


selected_classes = None
# selected_classes = [0, 1]
# selected_classes = [5,6]
# selected_classes = [5, 6, 7, 8]
# selected_classes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 32]

nd = True
# nd = False

baradel_split = True
actions = True # this is used to add an action annotation in the epic split files

bad_uids = [126, 961, 5099, 12599, 21740, 25710, 26811, 28585, 33647, 37431]
unavailable = [9, 11, 18]
available_pids = ["P{:02d}".format(i) for i in range(1,32) if i not in unavailable]

assert len(available_pids) == 28
if baradel_split:
    split_1 = {}
    for i in range(len(available_pids)):
        split_1[available_pids[i]] = "train" if i < 26 else "val" # Note:23/6/19.this is a bug. The actual baradel split is my previous split1
    split_dicts = [split_1]
else:
    split_1, split_2, split_3, split_4 = {}, {}, {}, {}
    for i in range(28):
        split_1[available_pids[i]] = "train" if i < 21 else "val"
        split_2[available_pids[i]] = "train" if i < 14 or i > 20 else "val"
        split_3[available_pids[i]] = "train" if i < 7 or i > 13 else "val"
        split_4[available_pids[i]] = "train" if i > 6 else "val"
    split_dicts = [split_1, split_2, split_3, split_4]

BASE_DIR = r"frames_rgb_flow\rgb\train"
SPLITS_DIR = r"..\..\splits\epic_rgb"
# SPLITS_DIR = r"..\..\splits\epic_rgb_select2_01"
# SPLITS_DIR = r"..\..\splits\epic_rgb_select24"
# SPLITS_DIR = r"..\..\splits\epic_rgb_select2_56"
if nd:
    SPLITS_DIR += '_nd'
if baradel_split:
    SPLITS_DIR += '_brd'
if actions:
    SPLITS_DIR += '_act'
    ACTIONS_FILE = r"D:\Datasets\egocentric\EPIC_KITCHENS\EPIC_action_classes.csv"
    all_action_ids = pandas.read_csv(ACTIONS_FILE)
os.makedirs(SPLITS_DIR, exist_ok=True)

train_names = [os.path.join(SPLITS_DIR, "epic_rgb_train_{}.txt".format(i)) for i in range(1, len(split_dicts) + 1)] # in range(1,5)
val_names = [os.path.join(SPLITS_DIR, "epic_rgb_val_{}.txt".format(i)) for i in range(1, len(split_dicts) + 1)]

train_files = []
val_files = []
for i in range(len(split_dicts)):
    train_files.append(open(train_names[i], 'a'))
    val_files.append(open(val_names[i], 'a'))

ANNOTATION_FILE = r"D:\Datasets\egocentric\EPIC_KITCHENS\EPIC_train_action_labels.csv"
annotations = pandas.read_csv(ANNOTATION_FILE)
for index, row in annotations.iterrows():
    start_frame = row.start_frame
    stop_frame = row.stop_frame
    num_frames = stop_frame - start_frame
    verb_class = row.verb_class
    if selected_classes:
       if verb_class not in selected_classes:
           continue
    noun_class = row.noun_class
    pid = row.participant_id
    uid = row.uid
    if nd and uid in bad_uids:
        continue
    if actions:
        action_id = all_action_ids[all_action_ids.class_key == '{}_{}'.format(verb_class, noun_class)].action_id.item()
    videoid = row.video_id
    action_dir = os.path.join(BASE_DIR, pid, videoid)
    if actions:
        line = "{} {} {} {} {} {} {}\n".format(action_dir, num_frames, verb_class, noun_class, uid, start_frame, action_id)
    else:
        line = "{} {} {} {} {} {}\n".format(action_dir, num_frames, verb_class, noun_class, uid, start_frame)
    for i in range(len(split_dicts)):
        split = split_dicts[i][pid]
        if split == 'train':
            train_files[i].write(line)
        else:
            val_files[i].write(line)

for i in range(len(split_dicts)):
    train_files[i].close()
    val_files[i].close()