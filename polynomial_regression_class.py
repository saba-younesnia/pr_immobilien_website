import pandas as pd
import numpy as np

class RealEstateModel:
    def __init__(self, file_path, tolerance=1e-5):
        self.df=pd.read_csv(file_path)
        self.tolerance=tolerance
        self.df=pd.read_csv(file_path)
        self.file_path=file_path

    def find_nearest_area(self, lat, lon):
        distances=np.sqrt((self.df['latitude']-lat)**2 + (self.df['longitude']-lon)**2)
        nearest_index=distances.idxmin()
        return self.df.loc[nearest_index]

    def get_nearest_latitude(self, lat, lon):
        nearest_area = self.find_nearest_area(lat, lon)
        return nearest_area['latitude']

    def get_nearest_longitude(self, lat, lon):
        nearest_area = self.find_nearest_area(lat, lon)
        return nearest_area['longitude']

    def create_filtered_df(self, latitude, longitude):
        nearest_area=self.find_nearest_area(latitude, longitude)
        filtered_df=self.df[(np.abs(self.df['latitude']-nearest_area['latitude']) < self.tolerance) & (np.abs(self.df['longitude']-nearest_area['longitude']) < self.tolerance)]
        return filtered_df

    def expand_dataset(self,latitude, longitude,year):
        df=self.create_filtered_df(latitude, longitude)
        filtered_df = df[(df['latitude'] == latitude) &
                         (df['longitude'] == longitude) &
                         (df['year'] == year)]
        result_df = filtered_df[['villa_min', 'property_number']]
        return result_df

    def create_model_villa_min(self, latitude, longitude):
        filtered_df1=self.create_filtered_df(latitude, longitude)
        filtered_df=filtered_df1.dropna(subset='villa_min')
        years=filtered_df['year'].tolist()
        villa_mins=filtered_df['villa_min'].tolist()
        model=np.poly1d(np.polyfit(years, villa_mins, 4))
        return model

    def predict_villa_min(self, year, latitude, longitude):
        model=self.create_model_villa_min(latitude, longitude)
        return model(year)

    def create_model_villa_max(self, latitude, longitude):
        filtered_df1 = self.create_filtered_df(latitude, longitude)
        filtered_df = filtered_df1.dropna(subset='villa_max')
        years = filtered_df['year'].tolist()
        villa_maxes = filtered_df['villa_max'].tolist()
        model = np.poly1d(np.polyfit(years, villa_maxes, 4))
        return model

    def predict_villa_max(self, year, latitude, longitude):
        model = self.create_model_villa_max(latitude, longitude)
        return model(year)

    def create_model_apartment_min(self, latitude, longitude):
        filtered_df1 = self.create_filtered_df(latitude, longitude)
        filtered_df = filtered_df1.dropna(subset='apartment_min')
        years = filtered_df['year'].tolist()
        apartment_mins = filtered_df['apartment_min'].tolist()
        model = np.poly1d(np.polyfit(years, apartment_mins, 4))
        return model

    def predict_apartment_min(self, year, latitude, longitude):
        model = self.create_model_apartment_min(latitude, longitude)
        return model(year)

    def create_model_apartment_max(self, latitude, longitude):
        filtered_df1 = self.create_filtered_df(latitude, longitude)
        filtered_df = filtered_df1.dropna(subset='apartment_max')
        years = filtered_df['year'].tolist()
        apartment_maxes = filtered_df['apartment_max'].tolist()
        model = np.poly1d(np.polyfit(years, apartment_maxes, 4))
        return model

    def predict_apartment_max(self, year, latitude, longitude):
        model = self.create_model_apartment_max(latitude, longitude)
        return model(year)

    def create_model_land_min(self, latitude, longitude):
        filtered_df1 = self.create_filtered_df(latitude, longitude)
        filtered_df = filtered_df1.dropna(subset='land_min')
        years = filtered_df['year'].tolist()
        land_mins = filtered_df['land_min'].tolist()
        model = np.poly1d(np.polyfit(years, land_mins, 4))
        return model

    def predict_land_min(self, year, latitude, longitude):
        model = self.create_model_land_min(latitude, longitude)
        return model(year)

    def create_model_land_max(self, latitude, longitude):
        filtered_df1 = self.create_filtered_df(latitude, longitude)
        filtered_df = filtered_df1.dropna(subset='land_max')
        years = filtered_df['year'].tolist()
        land_maxes = filtered_df['land_max'].tolist()
        model = np.poly1d(np.polyfit(years, land_maxes, 4))
        return model

    def predict_land_max(self, year, latitude, longitude):
        model = self.create_model_land_max(latitude, longitude)
        return model(year)


    def add_row_and_save(self, latitude, longitude, year=np.nan, villa_min=np.nan, villa_max=np.nan, land_min=np.nan, land_max=np.nan, apartment_min=np.nan, apartment_max=np.nan, property_number=np.nan):
        nearest_area = self.find_nearest_area(latitude, longitude)
        new_row = {
            'latitude': nearest_area['latitude'],
            'longitude': nearest_area['longitude'],
            'year': year,
            'villa_min': villa_min,
            'villa_max': villa_max,
            'land_min': land_min,
            'land_max': land_max,
            'apartment_min': apartment_min,
            'apartment_max': apartment_max,
            'property_number':property_number
        }
        self.df = self.df._append(new_row, ignore_index=True)
        self.df.to_csv(self.file_path, index=False)


