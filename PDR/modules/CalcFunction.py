import numpy as np
import pandas as pd


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def mean_angles(angle_list1, angle_list2, alpha=0.5):
    complex_list = alpha * np.exp(1j*angle_list1) + \
        (1-alpha) * np.exp(1j*angle_list2)
    mean_angle_list = np.angle(complex_list)
    return mean_angle_list


def diff_angles(angle1, angle2):
    diff_angle = np.arccos(np.cos(angle1)*np.cos(angle2) +
                           np.sin(angle1)*np.sin(angle2))
    return diff_angle


def rot_angles(angle1, angle2):
    rot_angle = np.arcsin(np.cos(angle1) * np.sin(angle2) -
                          np.sin(angle1) * np.cos(angle2))
    return rot_angle


def getRotationMatrixFromVector(rotation_vector, return_size):
    q1 = rotation_vector[0]
    q2 = rotation_vector[1]
    q3 = rotation_vector[2]
    q0 = rotation_vector[3]

    sq_q1 = 2 * q1 * q1
    sq_q2 = 2 * q2 * q2
    sq_q3 = 2 * q3 * q3
    q1_q2 = 2 * q1 * q2
    q3_q0 = 2 * q3 * q0
    q1_q3 = 2 * q1 * q3
    q2_q0 = 2 * q2 * q0
    q2_q3 = 2 * q2 * q3
    q1_q0 = 2 * q1 * q0

    if return_size == 16:
        rotation_matrix = np.zeros(16)
        rotation_matrix[0] = 1 - sq_q2 - sq_q3
        rotation_matrix[1] = q1_q2 - q3_q0
        rotation_matrix[2] = q1_q3 + q2_q0

        rotation_matrix[4] = q1_q2 + q3_q0
        rotation_matrix[5] = 1 - sq_q1 - sq_q3
        rotation_matrix[6] = q2_q3 - q1_q0

        rotation_matrix[8] = q1_q3 - q2_q0
        rotation_matrix[9] = q2_q3 + q1_q0
        rotation_matrix[10] = 1 - sq_q1 - sq_q2

        rotation_matrix[15] = 1

        rotation_matrix = rotation_matrix.reshape([4, 4])
    elif return_size == 9:
        rotation_matrix = np.zeros(9)
        rotation_matrix[0] = 1 - sq_q2 - sq_q3
        rotation_matrix[1] = q1_q2 - q3_q0
        rotation_matrix[2] = q1_q3 + q2_q0

        rotation_matrix[3] = q1_q2 + q3_q0
        rotation_matrix[4] = 1 - sq_q1 - sq_q3
        rotation_matrix[5] = q2_q3 - q1_q0

        rotation_matrix[6] = q1_q3 - q2_q0
        rotation_matrix[7] = q2_q3 + q1_q0
        rotation_matrix[8] = 1 - sq_q1 - sq_q2
        rotation_matrix = rotation_matrix.reshape([3, 3])

    return rotation_matrix


def getOrientation(rotation_matrix):
    orientation = np.zeros(3)  # Azimuth, pitch, roll
    orientation[0] = np.arctan2(rotation_matrix[0][1], rotation_matrix[1][1])
    orientation[1] = np.arcsin(-rotation_matrix[2][1])
    orientation[2] = np.arctan2(-rotation_matrix[2][0], rotation_matrix[2][2])
    return orientation


def pdr_to_displacement(pdr_df, heading_array):
    displacement_df = pd.DataFrame(
        columns=('body_x', 'body_y', 'nav_x', 'nav_y', 'rot_x', 'rot_y', 'game_x', 'game_y', 'fusion_x', 'fusion_y'))
    heading = heading_array[list(map(int, pdr_df['idx']))]
    displacement_df['body_x'] = pdr_df['length'] * np.cos(heading[:, 1])
    displacement_df['body_y'] = pdr_df['length'] * np.sin(heading[:, 1])
    displacement_df['nav_x'] = pdr_df['length'] * np.cos(heading[:, 2])
    displacement_df['nav_y'] = pdr_df['length'] * np.sin(heading[:, 2])
    displacement_df['rot_x'] = pdr_df['length'] * np.cos(heading[:, 3])
    displacement_df['rot_y'] = pdr_df['length'] * np.sin(heading[:, 3])
    displacement_df['game_x'] = pdr_df['length'] * np.cos(heading[:, 4])
    displacement_df['game_y'] = pdr_df['length'] * np.sin(heading[:, 4])
    displacement_df['fusion_x'] = pdr_df['length'] * np.cos(heading[:, 5])
    displacement_df['fusion_y'] = pdr_df['length'] * np.sin(heading[:, 5])
    return displacement_df
