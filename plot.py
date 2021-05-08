import argparse
import matplotlib.pyplot as plt

def plot(fps, time):

    # Find the limits
    # x_max, x_min = max(time)+1, min(time)
    # y_max, y_min = int(max(fps)+1), int(min(fps))

    # plotting the points
    color = ["green", "red", "blue"]
    marker = ['o', '+', '*']
    labels = ['MPTCP', 'UDP', 'Default']
    for i in range(0, len(fps)):
        plt.plot(time[i], fps[i], color=color[i], label=labels[i], linewidth = 1,
                marker=marker[i], markerfacecolor='blue', markersize=5)
    
    # setting x and y axis range
    plt.ylim(9, 11)
    plt.xlim(0, 55)
    
    # naming the x axis
    plt.xlabel('Time elapsed (in sec)')
    # naming the y axis
    plt.ylabel('FPS (Frames per second)')
    
    # giving a title to my graph
    plt.title('Comparison MPTCP Vs UDP')
    # function to show the plot
    plt.legend()
    plt.show()

def readFile(filenames):
    
    fps = []
    time = []

    for filename in filenames:
        fps_tmp = []
        time_tmp = []
        with open(filename, 'r') as fd:
            while True:
                line = fd.readline()
                if not line:
                    break

                line = line.strip().split(' ')
                fps_tmp.append(float(line[0]))
                time_tmp.append(float(line[1]))
        fd.close()
        fps.append(fps_tmp)
        time.append(time_tmp)
        
    plot(fps, time)  

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read data from file and plot graphs')
    parser.add_argument('-f', help='Error: Use plot.py -f filename', nargs="+")
    args = parser.parse_args()
    readFile(args.f)