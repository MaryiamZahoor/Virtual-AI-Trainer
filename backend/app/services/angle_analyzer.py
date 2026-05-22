import numpy as np
from typing import Tuple, List


class AngleAnalyzer:
    """Calculate angles between three keypoints"""
    
    @staticmethod
    def calculate_angle(
        point1: Tuple[float, float],
        point2: Tuple[float, float],
        point3: Tuple[float, float],
    ) -> float:
        """
        Calculate angle at point2 formed by point1-point2-point3
        
        Args:
            point1: (x, y) coordinates of first point
            point2: (x, y) coordinates of vertex (where angle is measured)
            point3: (x, y) coordinates of third point
            
        Returns:
            Angle in degrees (0-180)
        """
        # Convert points to numpy arrays
        p1 = np.array(point1)
        p2 = np.array(point2)
        p3 = np.array(point3)
        
        # Create vectors from point2 to point1 and point2 to point3
        v1 = p1 - p2  # Vector from vertex to point1
        v2 = p3 - p2  # Vector from vertex to point3
        
        # Calculate dot product and magnitudes
        dot_product = np.dot(v1, v2)
        magnitude_v1 = np.linalg.norm(v1)
        magnitude_v2 = np.linalg.norm(v2)
        
        # Avoid division by zero
        if magnitude_v1 == 0 or magnitude_v2 == 0:
            return 0.0
        
        # Calculate cosine of angle
        cos_angle = dot_product / (magnitude_v1 * magnitude_v2)
        
        # Clip to [-1, 1] to handle floating point errors
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        
        # Convert to angle in degrees
        angle_rad = np.arccos(cos_angle)
        angle_deg = np.degrees(angle_rad)
        
        return float(angle_deg)
    
    @staticmethod
    def get_distance(
        point1: Tuple[float, float],
        point2: Tuple[float, float],
    ) -> float:
        """Calculate Euclidean distance between two points"""
        p1 = np.array(point1)
        p2 = np.array(point2)
        return float(np.linalg.norm(p1 - p2))


# Global instance for use throughout the app
analyzer = AngleAnalyzer()