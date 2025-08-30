import cv2
import numpy as np
from scipy import signal
from scipy.ndimage import gaussian_filter1d
import json
import os
from typing import List, Dict, Tuple

class InterestPointExtractor:
    def __init__(self, min_prominence: float = 0.1, min_distance: int = 5):
        self.min_prominence = min_prominence
        self.min_distance = min_distance
    
    def identify_visual_type(self, image: np.ndarray) -> str:
        """
        Identifie le type de visuel (graphique 2D, histogramme, etc.)
        """
        if image is None:
            return "unknown"
        
        # Conversion en niveaux de gris
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Détection des contours
        edges = cv2.Canny(gray, 50, 150)
        
        # Détection des lignes avec HoughLinesP
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=50, maxLineGap=10)
        
        if lines is not None and len(lines) > 10:
            # Nombre significatif de lignes détectées → probablement un graphique
            return "graph2D"
        else:
            # Vérifier si c'est un histogramme
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            if np.var(hist) > 1000:  # Seuil empirique
                return "histogram"
            else:
                return "unknown"
    
    def define_targets(self, visual_type: str) -> List[str]:
        """
        Définit les cibles (types de points d'intérêt) en fonction du type de visuel
        """
        if visual_type == "graph2D":
            return ["maxima", "minima", "inflection_points", "sharp_changes"]
        elif visual_type == "histogram":
            return ["peaks", "valleys", "plateaus"]
        else:
            return ["salient_points"]
    
    def extract_points_with_cv(self, image: np.ndarray, targets: List[str]) -> List[Tuple[int, int]]:
        """
        Extrait les points d'intérêt avec les techniques de vision par ordinateur
        """
        points = []
        if image is None:
            return points
            
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Détection des coins avec Shi-Tomasi
        if "sharp_changes" in targets or "salient_points" in targets:
            corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.01, minDistance=10)
            if corners is not None:
                for corner in corners:
                    x, y = corner.ravel()
                    points.append((int(x), int(y), "corner"))
        
        # Détection des contours
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # Approximation du contour
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            for point in approx:
                x, y = point.ravel()
                points.append((int(x), int(y), "contour_feature"))
        
        return points
    
    def extract_points_with_stats(self, data: np.ndarray, targets: List[str]) -> List[Tuple[int, int]]:
        """
        Extrait les points d'intérêt avec des techniques statistiques
        """
        points = []
        
        if data is None or len(data) == 0:
            return points
        
        # Conversion des données NumPy en liste Python
        if isinstance(data, np.ndarray):
            data = data.tolist()
        
        # Lissage des données
        smoothed_data = gaussian_filter1d(data, sigma=2)
        
        # Calcul de la dérivée première
        first_derivative = np.gradient(smoothed_data)
        
        # Calcul de la dérivée seconde
        second_derivative = np.gradient(first_derivative)
        
        # Détection des maxima et minima
        if "maxima" in targets or "minima" in targets or "peaks" in targets or "valleys" in targets:
            peak_indices, _ = signal.find_peaks(smoothed_data, prominence=self.min_prominence, distance=self.min_distance)
            valley_indices, _ = signal.find_peaks(-smoothed_data, prominence=self.min_prominence, distance=self.min_distance)
            
            for idx in peak_indices:
                # Conversion des types NumPy en types Python natifs
                points.append((int(idx), float(smoothed_data[idx]), "maximum"))
            
            for idx in valley_indices:
                # Conversion des types NumPy en types Python natifs
                points.append((int(idx), float(smoothed_data[idx]), "minimum"))
        
        # Détection des points d'inflexion
        if "inflection_points" in targets:
            # Les points d'inflexion sont où la dérivée seconde change de signe
            sign_changes = np.where(np.diff(np.sign(second_derivative)))[0]
            for idx in sign_changes:
                # Conversion des types NumPy en types Python natifs
                points.append((int(idx), float(smoothed_data[idx]), "inflection"))
        
        return points
    
    def filter_points(self, points: List[Tuple], visual_type: str) -> List[Tuple]:
        """
        Filtre les points d'intérêt pour éliminer les faux positifs
        """
        filtered_points = []
        
        # Filtrage basé sur le type de visuel
        if visual_type == "graph2D":
            # Pour les graphiques 2D, on garde les points avec une certaine prominence
            for point in points:
                if point[2] in ["maximum", "minimum", "inflection"]:
                    filtered_points.append(point)
        elif visual_type == "histogram":
            # Pour les histogrammes, on garde les pics et vallées significatifs
            for point in points:
                if point[2] in ["maximum", "minimum"]:
                    filtered_points.append(point)
        
        # Suppression des doublons (points proches)
        unique_points = []
        for point in filtered_points:
            is_duplicate = False
            for unique_point in unique_points:
                if abs(point[0] - unique_point[0]) < self.min_distance:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_points.append(point)
        
        return unique_points
    
    def associate_with_data(self, points: List[Tuple], extracted_data: Dict) -> List[Dict]:
        """
        Associe les points visuels aux valeurs concrètes extraites
        """
        associated_points = []
        
        for point in points:
            x_idx, y_val, point_type = point
            
            # Trouver la valeur x correspondante
            if extracted_data and "x_values" in extracted_data and x_idx < len(extracted_data["x_values"]):
                x_val = extracted_data["x_values"][x_idx]
                # Conversion des types NumPy en types Python natifs
                if hasattr(x_val, 'item'):
                    x_val = x_val.item()
            else:
                x_val = x_idx
            
            # Conversion des types NumPy en types Python natifs
            if hasattr(y_val, 'item'):
                y_val = y_val.item()
            
            associated_points.append({
                "type": point_type,
                "x_index": x_idx,
                "x_value": x_val,
                "y_value": y_val
            })
        
        return associated_points
    
    def generate_structured_output(self, points: List[Dict]) -> str:
        """
        Génère un format JSON contenant les informations sur les points d'intérêt
        """
        # Conversion des types NumPy en types Python natifs
        serializable_points = []
        for point in points:
            serializable_point = {}
            for key, value in point.items():
                if hasattr(value, 'item'):
                    serializable_point[key] = value.item()
                else:
                    serializable_point[key] = value
            serializable_points.append(serializable_point)
        
        output = {
            "interest_points": serializable_points,
            "count": len(serializable_points),
            "extraction_method": "combined_cv_statistical"
        }
        
        return json.dumps(output, indent=2)
    
    def process_image(self, image: np.ndarray, extracted_data: Dict = None) -> str:
        """
        Pipeline complet de traitement d'image pour l'extraction des points d'intérêt
        """
        # Vérifier si l'image est valide
        if image is None:
            return json.dumps({"error": "Image non valide ou impossible à charger"})
        
        # Étape 2: Identification du type de visuel
        visual_type = self.identify_visual_type(image)
        
        # Étape 3: Définition des cibles
        targets = self.define_targets(visual_type)
        
        # Étape 4: Extraction des points avec techniques combinées
        cv_points = self.extract_points_with_cv(image, targets)
        
        # Si des données numériques sont disponibles, extraction statistique
        stat_points = []
        if extracted_data and "y_values" in extracted_data:
            y_data = extracted_data["y_values"]
            # Conversion des types NumPy en types Python natifs
            if hasattr(y_data, 'tolist'):
                y_data = y_data.tolist()
            stat_points = self.extract_points_with_stats(y_data, targets)
        
        # Combinaison des points
        all_points = cv_points + stat_points
        
        # Étape 5: Filtrage des points
        filtered_points = self.filter_points(all_points, visual_type)
        
        # Étape 6: Association avec les données extraites
        if extracted_data:
            associated_points = self.associate_with_data(filtered_points, extracted_data)
        else:
            # Conversion des points en format de dictionnaire si pas de données extraites
            associated_points = []
            for p in filtered_points:
                x_val, y_val = p[0], p[1]
                # Conversion des types NumPy en types Python natifs
                if hasattr(x_val, 'item'):
                    x_val = x_val.item()
                if hasattr(y_val, 'item'):
                    y_val = y_val.item()
                associated_points.append({"x": x_val, "y": y_val, "type": p[2]})
        
        # Étape 7: Génération de la sortie structurée
        json_output = self.generate_structured_output(associated_points)
        
        return json_output

# Exemple d'utilisation
if __name__ == "__main__":
    # Vérifier et corriger le chemin d'accès à l'image
    image_path = "C:/Users/ProBook/Desktop/stage/diagrammeex.jpeg"
    
    # Vérifier si le fichier existe
    if not os.path.exists(image_path):
        print(f"Erreur: Le fichier {image_path} n'existe pas.")
        print("Veuillez vérifier le chemin d'accès et le nom du fichier.")
        
        # Créer une image de test pour la démonstration
        print("Création d'une image de test pour la démonstration...")
        image = np.ones((400, 600, 3), dtype=np.uint8) * 255  # Fond blanc
        
        # Dessiner un graphique simple
        points = np.array([[100, 300], [200, 200], [300, 350], [400, 250], [500, 320]], np.int32)
        cv2.polylines(image, [points], False, (0, 0, 255), 2)
        
        # Ajouter des axes
        cv2.line(image, (50, 50), (50, 350), (0, 0, 0), 2)  # Axe Y
        cv2.line(image, (50, 350), (550, 350), (0, 0, 0), 2)  # Axe X
    else:
        # Charger l'image
        image = cv2.imread("C:/Users/ProBook/Desktop/stage/diagrammeex.jpeg")
        if image is None:
            print(f"Erreur: Impossible de charger l'image à partir de {image_path}")
            exit(1)
    
    # Données extraites (simulées, normalement de l'étape d'extraction graphique)
    extracted_data = {
        "x_values": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "y_values": [1, 3, 2, 5, 4, 7, 6, 8, 7, 9, 10]
    }
    
    # Initialiser l'extracteur
    extractor = InterestPointExtractor(min_prominence=0.5, min_distance=3)
    
    # Traiter l'image
    result_json = extractor.process_image(image, extracted_data)
    
    print("Points d'intérêt extraits:")
    print(result_json)
    
    # Étape 8: Transmission au LLM (serait fait dans une autre partie du pipeline)
    # llm_analyzer.analyze_points(json.loads(result_json))