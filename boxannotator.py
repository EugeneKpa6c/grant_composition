import cv2
import numpy as np


class BoxAnnotator:
    """
    Класс для рисования ограничивающих рамок на изображении с использованием предоставленных средств обнаружения.

    Атрибуты:
        толщина (int): толщина линий ограничивающего прямоугольника, по умолчанию равна 2
        text_scale (float): масштаб текста в ограничивающей рамке, по умолчанию равен 0,5
        text_thickness (int): толщина текста в ограничивающей рамке, по умолчанию равна 1
        text_padding (int): Отступ вокруг текста в ограничивающей рамке, по умолчанию равен 5

    """

    def __init__(
        self,
        thickness: int = 2,
        text_scale: float = 0.5,
        text_thickness: int = 1,
        text_padding: int = 10,
    ):
        self.thickness: int = thickness
        self.text_scale: float = text_scale
        self.text_thickness: int = text_thickness
        self.text_padding: int = text_padding
    
    def annotate(
        self,
        scene: np.ndarray,
        detections: list,
        # labels: Optional[List[str]] = None,
        skip_label: bool = False,
    ) -> np.ndarray:
        """
        Рисует ограничивающие рамки на рамке, используя предоставленные средства обнаружения.

        Аргументы:
            scene (np.ndarray): Изображение, на котором будут нарисованы ограничивающие рамки
            detections (Detections): обнаружения, для которых будут нарисованы ограничивающие рамки
            labels (необязательно[Список[str]]): Необязательный список меток, соответствующих каждому обнаружению. Если `метки" не указаны, в качестве метки будет использоваться соответствующий "class_id".
            skip_label (bool): установлено значение `True`, пропускается аннотация к метке ограничивающего прямоугольника.
        Возвращается:
            np.ndarray: изображение с нарисованными на нем ограничивающими рамками

        """
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        x1, y1, x2, y2 = self.xywh_to_xyxy(detections) #.astype(int)
        x1 = int(x1)
        x2 = int(x2)
        y1 = int(y1)
        y2 = int(y2)

        cv2.rectangle(
            img=scene,
            pt1=(x1, y1),
            pt2=(x2, y2),
            color=(255, 0, 0),
            thickness=self.thickness,
        )

        return scene

    def xywh_to_xyxy(self,input_array):
        x = input_array[0]
        y = input_array[1]
        width = input_array[2]
        height = input_array[3]
        
        x1 = x - width / 2
        y1 = y + height / 2
        x2 = x + width / 2
        y2 = y - height / 2
        
        corners = [x1, y1, x2, y2]
        return corners