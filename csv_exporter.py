import pandas as pd


class CSVExporter:
    def __init__(self, filename="appointments.csv"):
        self.filename = filename

    def export(self, data):
        pd.DataFrame(data).to_csv(
            self.filename, index=False, header=["Date", "Time", "Location"]
        )
