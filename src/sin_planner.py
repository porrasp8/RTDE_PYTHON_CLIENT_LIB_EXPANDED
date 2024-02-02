import numpy as np
import time
import matplotlib.pyplot as plt

class PathPlanSine(object):
    def __init__(self, pose_init, pose_desired, total_time):
        self.position_init = pose_init[:3]
        self.position_des = pose_desired[:3]
        self.tfinal = total_time

    def trajectory_planning(self, t):
        X_init, Y_init, Z_init = self.position_init
        X_final, Y_final, Z_final = self.position_des

        x_traj = 0.5 * (X_final - X_init) * (1 - np.cos(2 * np.pi * t / self.tfinal)) + X_init
        y_traj = 0.5 * (Y_final - Y_init) * (1 - np.cos(2 * np.pi * t / self.tfinal)) + Y_init
        z_traj = 0.5 * (Z_final - Z_init) * (1 - np.cos(2 * np.pi * t / self.tfinal)) + Z_init
        position = np.array([x_traj, y_traj, z_traj])

        vx = 0.5 * (X_final - X_init) * (2 * np.pi / self.tfinal) * np.sin(2 * np.pi * t / self.tfinal)
        vy = 0.5 * (Y_final - Y_init) * (2 * np.pi / self.tfinal) * np.sin(2 * np.pi * t / self.tfinal)
        vz = 0.5 * (Z_final - Z_init) * (2 * np.pi / self.tfinal) * np.sin(2 * np.pi * t / self.tfinal)
        velocity = np.array([vx, vy, vz])

        ax = 0.5 * (X_final - X_init) * (2 * np.pi / self.tfinal) ** 2 * np.cos(2 * np.pi * t / self.tfinal)
        ay = 0.5 * (Y_final - Y_init) * (2 * np.pi / self.tfinal) ** 2 * np.cos(2 * np.pi * t / self.tfinal)
        az = 0.5 * (Z_final - Z_init) * (2 * np.pi / self.tfinal) ** 2 * np.cos(2 * np.pi * t / self.tfinal)
        acceleration = np.array([ax, ay, az])

        return [position, velocity, acceleration]

if __name__ == "__main__":
    pose_init = np.array([0.091, -0.34, 0.501])
    pose_des = np.array([0.4725, -0.071, 0.255])
    tfinal = 5

    trajectory = PathPlanSine(pose_init, pose_des, tfinal)

    posx, posy, posz = [], [], []
    v_x, v_y, v_z = [], [], []
    a_x, a_y, a_z = [], [], []
    time_range = []

    t_start = time.time()
    while time.time() - t_start < tfinal:
        t_current = time.time() - t_start
        [position, velocity, acceleration] = trajectory.trajectory_planning(t_current)

        posx.append(position[0])
        posy.append(position[1])
        posz.append(position[2])

        v_x.append(velocity[0])
        v_y.append(velocity[1])
        v_z.append(velocity[2])

        a_x.append(acceleration[0])
        a_y.append(acceleration[1])
        a_z.append(acceleration[2])

        time_range.append(t_current)

    # Plotear con pyplot
    plt.figure()
    plt.plot(time_range, posx, label='X position')
    plt.plot(time_range, posy, label='Y position')
    plt.plot(time_range, posz, label='Z position')
    plt.legend()
    plt.grid()
    plt.ylabel('Position [m]')
    plt.xlabel('Time [s]')

    plt.figure()
    plt.plot(time_range, v_x, label='X velocity')
    plt.plot(time_range, v_y, label='Y velocity')
    plt.plot(time_range, v_z, label='Z velocity')
    plt.legend()
    plt.grid()
    plt.ylabel('Velocity[m/s]')
    plt.xlabel('Time [s]')

    plt.figure()
    plt.plot(time_range, a_x, label='X acc')
    plt.plot(time_range, a_y, label='Y acc')
    plt.plot(time_range, a_z, label='Z acc')
    plt.legend()
    plt.grid()
    plt.ylabel('Acceleration [m/s^2]')
    plt.xlabel('Time [s]')
    plt.show()
