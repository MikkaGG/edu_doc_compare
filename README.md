## Выпускная квалификационная работа. ##

1) Читаются учебные планы в формате pdf, к ним строятся emedding'и и сохраняются в векторную базу данных ChromaDB.
2) Применяется OCR для отсканированнной справки об обучении студента, строится embedding и при помощи косинусного расстояния находятся наиболее похожий план обучения.
3) Сопоставляются предметы из найденного учебного плана и справки об обучении для расчета разницы учебных часов.

Для создания emeddings применялась модель deepvk/USER-bge-m3 (https://huggingface.co/deepvk/USER-bge-m3).
