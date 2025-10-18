"""
Track configuration and data
Defines the circuit layout, teams, and drivers
"""
import math
from typing import List
from models import TrackConfig, TrackPoint, Sector, DRSZone, Position, Team


def generate_track_points() -> List[TrackPoint]:
    """
    Generate track points for the F1 circuit
    Non-overlapping layout that fits within 1000x700 canvas
    """
    points: List[TrackPoint] = []
    
    # Canvas dimensions: 1000x700 with padding
    PADDING = 60
    
    # START/FINISH STRAIGHT (Bottom of track)
    # Sector 1 starts here
    start_y = 550  # Moved down to give space at top
    for i in range(25):
        points.append(TrackPoint(x=150 + i * 16, y=start_y, sector=1))
    
    # TURN 1 - Right-hand sweeping corner
    for i in range(20):
        angle = (i / 19) * math.pi * 0.5
        points.append(TrackPoint(
            x=550 + math.sin(angle) * 100,
            y=start_y - (1 - math.cos(angle)) * 100,
            sector=1
        ))
    
    # BACK STRAIGHT going up (right side of track)
    for i in range(30):
        points.append(TrackPoint(x=650, y=450 - i * 10, sector=1))
    
    # TURN 2 - Hairpin at top (Sector 2 begins)
    for i in range(25):
        angle = (i / 24) * math.pi
        points.append(TrackPoint(
            x=650 - math.sin(angle) * 120,
            y=150 - math.cos(angle) * 120,
            sector=2
        ))
    
    # TOP STRAIGHT going left
    for i in range(35):
        points.append(TrackPoint(x=530 - i * 8, y=270, sector=2))
    
    # TURN 3 - Left-hander leading to middle section
    for i in range(18):
        angle = (i / 17) * math.pi * 0.5
        points.append(TrackPoint(
            x=250 - math.cos(angle) * 70,
            y=270 + math.sin(angle) * 70,
            sector=2
        ))
    
    # MIDDLE STRAIGHT (Sector 3 begins)
    for i in range(20):
        points.append(TrackPoint(x=180, y=340 + i * 5, sector=3))
    
    # TURN 4 - Chicane complex
    for i in range(25):
        angle = (i / 24) * math.pi
        offset = math.sin(angle * 3) * 35
        points.append(TrackPoint(
            x=180 - offset,
            y=440 + i * 2.5,
            sector=3
        ))
    
    # FINAL CORNER - Sweeping left onto start/finish
    for i in range(20):
        angle = (i / 19) * math.pi * 0.4
        points.append(TrackPoint(
            x=145 - math.sin(angle) * 60 + 60,
            y=502.5 + math.cos(angle) * 50,
            sector=3
        ))
    
    # Connect back to start/finish line
    for i in range(8):
        points.append(TrackPoint(
            x=145 + i * 0.625,
            y=start_y,
            sector=3
        ))
    
    return points


# Generate track points
TRACK_POINTS = generate_track_points()

# Define sectors
SECTORS = [
    Sector(
        id=1,
        name="Sector 1",
        start_index=0,
        end_index=int(len(TRACK_POINTS) * 0.35),
        length=1847
    ),
    Sector(
        id=2,
        name="Sector 2",
        start_index=int(len(TRACK_POINTS) * 0.35),
        end_index=int(len(TRACK_POINTS) * 0.70),
        length=1654
    ),
    Sector(
        id=3,
        name="Sector 3",
        start_index=int(len(TRACK_POINTS) * 0.70),
        end_index=len(TRACK_POINTS) - 1,
        length=1499
    ),
]

# DRS zones
DRS_ZONES = [
    DRSZone(
        id="drs_1",
        detection_point=0.92,
        activation_point=0.02,
        end_point=0.15
    ),
    DRSZone(
        id="drs_2",
        detection_point=0.35,
        activation_point=0.40,
        end_point=0.55
    ),
]

# Track configuration
TRACK_CONFIG = TrackConfig(
    name="Circuit de Strategie",
    country="International",
    total_length=5000,
    sectors=SECTORS,
    drs_zones=DRS_ZONES,
    pit_entry=Position(x=100, y=570),
    pit_exit=Position(x=400, y=570),
    start_line=Position(x=150, y=550),
    track_points=TRACK_POINTS
)

# Teams
TEAMS = [
    Team(id="RBR", name="Red Bull Racing", color="#0600ef"),
    Team(id="FER", name="Ferrari", color="#dc0000"),
    Team(id="MER", name="Mercedes", color="#00d2be"),
    Team(id="MCL", name="McLaren", color="#ff8700"),
    Team(id="AST", name="Aston Martin", color="#006f62"),
    Team(id="ALP", name="Alpine", color="#0090ff"),
    Team(id="WIL", name="Williams", color="#005aff"),
    Team(id="ATR", name="AlphaTauri", color="#2b4562"),
    Team(id="ALF", name="Alfa Romeo", color="#900000"),
    Team(id="HAS", name="Haas", color="#ffffff"),
]

# Driver names
DRIVER_NAMES = [
    "M. Verstappen",
    "S. Perez",
    "C. Leclerc",
    "C. Sainz",
    "L. Hamilton",
    "G. Russell",
    "L. Norris",
    "O. Piastri",
    "F. Alonso",
    "L. Stroll",
    "P. Gasly",
    "E. Ocon",
    "A. Albon",
    "L. Sargeant",
    "Y. Tsunoda",
    "D. Ricciardo",
    "V. Bottas",
    "Z. Guanyu",
    "K. Magnussen",
    "N. Hulkenberg",
]

