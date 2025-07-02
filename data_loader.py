import pandas as pd
import geopandas as gpd
import streamlit as st
from abc import ABC, abstractmethod
from typing import Tuple

class BaseDataLoader(ABC):
    def __init__(self, data_file: str, geometry_file: str):
        self.data_file = data_file
        self.geometry_file = geometry_file
    
    @abstractmethod
    def get_join_column(self) -> str:
        pass
    
    @abstractmethod
    def process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        pass
    
    def load_data(self) -> Tuple[gpd.GeoDataFrame, list]:
        try:
            df = pd.read_csv(self.data_file)
            gdf = gpd.read_file(self.geometry_file)
            df = self.process_data(df)
            join_col = self.get_join_column()
            
            if isinstance(join_col, list):
                for col in join_col:
                    df[col] = df[col].str.strip().str.title()
                    gdf[col] = gdf[col].str.strip().str.title()
                gdf = gdf[join_col + ['geometry']].drop_duplicates()
                merged = df.merge(gdf, on=join_col, how='left')
                
                # Create sector display names for selection
                if 'Sector' in merged.columns and 'District' in merged.columns:
                    merged['sector_display'] = merged['Sector'] + ' (' + merged['District'] + ')'
                    merged['sector_key'] = merged['Sector'] + '_' + merged['District']
                    options = sorted(merged['sector_display'].unique())
                else:
                    options = []
            else:
                gdf = gdf[[join_col, 'geometry']].drop_duplicates()
                merged = df.merge(gdf, on=join_col, how='left')
                options = sorted(merged[join_col].unique()) if isinstance(join_col, str) else []
            
            merged = gpd.GeoDataFrame(merged, geometry='geometry')
            return merged, options
        except Exception as e:
            st.error(f"Data loading failed: {e}")
            return None, []

class MalariaDataLoader(BaseDataLoader):
    def __init__(self):
        super().__init__('data/district_malaria_data.csv', 'data/district_geometries.geojson')
    
    def get_join_column(self):
        return 'District'
    
    def process_data(self, df):
        df['Date'] = pd.to_datetime(df['Date'])
        df['year'] = df['Date'].dt.year.astype('int32')
        df['month'] = df['Date'].dt.month.astype('int32')
        df['month_name'] = df['Date'].dt.strftime('%B')
        
        for col in ['Population', 'all cases', 'Severe cases/Deaths', 'all cases incidence', 'Severe cases/Deaths incidence']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df

class SectorDataLoader(BaseDataLoader):
    def __init__(self):
        super().__init__('data/sector_malaria_data.csv', 'data/sector_geometries.geojson')
    
    def get_join_column(self):
        return ['District', 'Sector']
    
    def process_data(self, df):
        df['Date'] = pd.to_datetime(df['Date'])
        df['year'] = df['Date'].dt.year.astype('int32')
        df['month'] = df['Date'].dt.month.astype('int32')
        df['month_name'] = df['Date'].dt.strftime('%B')
        
        for col in ['Population', 'Simple malaria cases', 'incidence']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df