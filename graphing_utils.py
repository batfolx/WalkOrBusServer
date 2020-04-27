import matplotlib.pyplot as plt
import database
import numpy


def _get_graph_data(num_day: int, db_results: list, boris_stats: dict, day_name: str):
    accuracy = []
    ax = []
    i = 0
    for result in db_results:
        if result['day'] == num_day:
            accuracy.append(float(result['accuracy']))
            ax.append(i)
            i += 1
    plt.plot(ax, accuracy)
    plt.xlabel(f"Number of data points on {day_name}")
    plt.ylabel("Accuracy in percent")
    plt.title(f"Accuracy over time for {day_name}")
    plt.yticks(numpy.arange(0, 110, 10))
    plt.grid()
    plt.savefig(f'images/boris_day_{day_name}.png')
    plt.show()


def boris_percentage_overall_graph():
    results = database.get_everything_from_db()
    accuracy = []
    timestamps = []
    counter = 0
    for result in results:
        accuracy.append(float(result['accuracy']))
        timestamps.append(counter)
        counter += 1

    fig = plt.plot(timestamps, accuracy)
    plt.ylabel(ylabel="Accuracy in %")
    plt.xlabel(xlabel=f"Time, starting from {results[0]['timestamp'][:10]} to {results[len(results)-1]['timestamp'][:10]}")
    plt.title("Boris percent correct vs time")
    plt.yticks(numpy.arange(0, 110, 10))
    plt.grid()
    plt.savefig("images/boris_graph.png")

    plt.show()
    return fig


def get_day_graph(day):
    results = database.get_everything_from_db()
    stats = database.get_boris_accuracy()
    if day == 'sunday':
        _get_graph_data(6, results, stats, day)
    if day == 'monday':
        _get_graph_data(0, results, stats, day)
    elif day == 'tuesday':
        _get_graph_data(1, results, stats, day)
    elif day == 'wednesday':
        _get_graph_data(2, results, stats, day)
    elif day == 'thursday':
        _get_graph_data(3, results, stats, day)
    elif day == 'friday':
        _get_graph_data(4, results, stats, day)
    elif day == 'saturday':
        _get_graph_data(5, results, stats, day)



#get_day_graph("monday")
#boris_percentage_overall_graph()

