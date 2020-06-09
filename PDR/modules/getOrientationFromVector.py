import numpy as np

def getRotationMatrixFromVector(rotationVector):
    R = np.zeros((4, 4))
    q1 = rotationVector[0]
    q2 = rotationVector[1]
    q3 = rotationVector[2]
    q0 = rotationVector[3]

    sq_q1 = 2 * q1 * q1
    sq_q2 = 2 * q2 * q2
    sq_q3 = 2 * q3 * q3
    q1_q2 = 2 * q1 * q2
    q3_q0 = 2 * q3 * q0
    q1_q3 = 2 * q1 * q3
    q2_q0 = 2 * q2 * q0
    q2_q3 = 2 * q2 * q3
    q1_q0 = 2 * q1 * q0

    R[0][0] = 1 - sq_q2 - sq_q3
    R[0][1] = q1_q2 - q3_q0
    R[0][2] = q1_q3 + q2_q0
    R[0][3] = 0.0

    R[1][0] = q1_q2 + q3_q0
    R[1][1] = 1 - sq_q1 - sq_q3
    R[1][2] = q2_q3 - q1_q0
    R[1][3] = 0.0

    R[2][0] = q1_q3 - q2_q0
    R[2][1] = q2_q3 + q1_q0
    R[2][2] = 1 - sq_q1 - sq_q2
    R[2][3] = 0.0

    R[3][0] = R[3][1] = R[3][2] = 0.0
    R[3][3] = 1.0
    return R


def getOrientation(R):
    eulerangle = [0, 0, 0]
    # yaw
    eulerangle[0] = np.arctan2(R[0][1], R[1][1])
    # pitch
    eulerangle[1] = np.arcsin(-R[2][1])
    # roll
    eulerangle[2] = np.arctan2(-R[2][0], R[2][2])

    return eulerangle
