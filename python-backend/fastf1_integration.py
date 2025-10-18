"""
FastF1 Integration Service
Provides access to real F1 data for enhanced simulation and strategy
"""
import os
from typing import Optional, Dict, List
import fastf1
import numpy as np
import pandas as pd
from fastf1 import plotting

from config import settings
from models import TireCompound


class FastF1Service:
    """
    Integration with FastF1 library for real F1 data
    Can be used for:
    - Historical race data analysis
    - Realistic tire degradation models
    - Lap time predictions
    - Strategy optimization based on real data
    """
    
    def __init__(self):
        # Set up cache directory
        os.makedirs(settings.FASTF1_CACHE_DIR, exist_ok=True)
        fastf1.Cache.enable_cache(settings.FASTF1_CACHE_DIR)
        
        # Enable plotting if needed
        plotting.setup_mpl()
        
        self.session_cache: Dict = {}
    
    async def load_session(
        self,
        year: int,
        race: str,
        session_type: str = 'R'
    ) -> Optional[fastf1.core.Session]:
        """
        Load an F1 session from FastF1
        
        Args:
            year: Season year (e.g., 2023)
            race: Race name or round number
            session_type: 'FP1', 'FP2', 'FP3', 'Q', 'S' (Sprint), 'R' (Race)
        
        Returns:
            FastF1 Session object
        """
        cache_key = f"{year}_{race}_{session_type}"
        
        if cache_key in self.session_cache:
            return self.session_cache[cache_key]
        
        try:
            session = fastf1.get_session(year, race, session_type)
            session.load()
            self.session_cache[cache_key] = session
            return session
        except Exception as e:
            print(f"Error loading FastF1 session: {e}")
            return None
    
    async def get_tire_degradation_model(
        self,
        year: int,
        race: str,
        compound: TireCompound
    ) -> Dict[str, float]:
        """
        Get tire degradation parameters from real F1 data
        
        Returns:
            Dictionary with degradation parameters
        """
        session = await self.load_session(year, race, 'R')
        if not session:
            return self._default_degradation_model()
        
        try:
            # Get laps on specified compound
            laps = session.laps
            compound_map = {
                TireCompound.SOFT: 'SOFT',
                TireCompound.MEDIUM: 'MEDIUM',
                TireCompound.HARD: 'HARD'
            }
            
            compound_laps = laps[laps['Compound'] == compound_map.get(compound, 'MEDIUM')]
            
            if len(compound_laps) == 0:
                return self._default_degradation_model()
            
            # Calculate degradation rate
            lap_times = compound_laps['LapTime'].dt.total_seconds()
            lap_numbers = compound_laps['TyreLife']
            
            # Simple linear regression for degradation
            if len(lap_times) > 5:
                coeffs = np.polyfit(lap_numbers, lap_times, 1)
                degradation_per_lap = coeffs[0]
            else:
                degradation_per_lap = 0.05  # Default 0.05s per lap
            
            return {
                'compound': compound.value,
                'degradation_per_lap': float(degradation_per_lap),
                'optimal_life': int(compound_laps['TyreLife'].max()) if len(compound_laps) > 0 else 20,
                'cliff_lap': int(compound_laps['TyreLife'].quantile(0.8)) if len(compound_laps) > 0 else 15
            }
            
        except Exception as e:
            print(f"Error calculating tire degradation: {e}")
            return self._default_degradation_model()
    
    async def get_optimal_strategy(
        self,
        year: int,
        race: str,
        current_lap: int,
        laps_remaining: int
    ) -> Dict:
        """
        Calculate optimal pit strategy based on historical data
        
        Returns:
            Strategy recommendation with pit windows and compounds
        """
        session = await self.load_session(year, race, 'R')
        if not session:
            return self._default_strategy(current_lap, laps_remaining)
        
        try:
            # Analyze pit stop strategies from real race
            results = session.results
            
            # Get pit stop data
            # This is simplified - real implementation would be more complex
            avg_pit_stops = 2  # Most F1 races have 1-2 pit stops
            
            pit_window_1 = int(laps_remaining * 0.33)
            pit_window_2 = int(laps_remaining * 0.66)
            
            return {
                'recommended_stops': avg_pit_stops,
                'pit_windows': [
                    {'lap_start': current_lap + pit_window_1 - 2, 'lap_end': current_lap + pit_window_1 + 2},
                    {'lap_start': current_lap + pit_window_2 - 2, 'lap_end': current_lap + pit_window_2 + 2},
                ],
                'compound_sequence': ['medium', 'hard'],
                'confidence': 0.75
            }
            
        except Exception as e:
            print(f"Error calculating strategy: {e}")
            return self._default_strategy(current_lap, laps_remaining)
    
    async def get_lap_time_prediction(
        self,
        year: int,
        race: str,
        compound: TireCompound,
        tire_age: int,
        fuel_load: float
    ) -> float:
        """
        Predict lap time based on compound, tire age, and fuel
        
        Returns:
            Predicted lap time in seconds
        """
        session = await self.load_session(year, race, 'R')
        if not session:
            return 90.0  # Default lap time
        
        try:
            # Get reference lap times
            laps = session.laps
            compound_map = {
                TireCompound.SOFT: 'SOFT',
                TireCompound.MEDIUM: 'MEDIUM',
                TireCompound.HARD: 'HARD'
            }
            
            # Filter for compound
            relevant_laps = laps[laps['Compound'] == compound_map.get(compound, 'MEDIUM')]
            
            if len(relevant_laps) == 0:
                return 90.0
            
            # Base lap time
            base_time = relevant_laps['LapTime'].dt.total_seconds().median()
            
            # Adjust for tire age
            degradation = tire_age * 0.05  # 0.05s per lap
            
            # Adjust for fuel (lighter = faster)
            fuel_effect = (100 - fuel_load) * 0.03  # 0.03s per % fuel reduction
            
            predicted_time = base_time + degradation - fuel_effect
            
            return float(predicted_time)
            
        except Exception as e:
            print(f"Error predicting lap time: {e}")
            return 90.0
    
    def _default_degradation_model(self) -> Dict[str, float]:
        """Default tire degradation model"""
        return {
            'compound': 'medium',
            'degradation_per_lap': 0.05,
            'optimal_life': 20,
            'cliff_lap': 15
        }
    
    def _default_strategy(self, current_lap: int, laps_remaining: int) -> Dict:
        """Default pit strategy"""
        return {
            'recommended_stops': 2,
            'pit_windows': [
                {'lap_start': current_lap + int(laps_remaining * 0.33), 'lap_end': current_lap + int(laps_remaining * 0.33) + 3}
            ],
            'compound_sequence': ['medium', 'hard'],
            'confidence': 0.5
        }


# Global instance
fastf1_service = FastF1Service()

