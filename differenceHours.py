import re
from sentence_transformers import SentenceTransformer, util
import numpy as np
import os
import logging
from subject_utils import extract_subject_name

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")

def extract_hours(subject_line):
    match = re.search(r'-\s*(\d+)\s*часов', subject_line, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def get_difference_hours(best_plan_extracted, extracted_text):
    output_lines = []
    
    logger.info("Сравнения предметов из учебной карточки и учебного плана")
    
    model = SentenceTransformer("deepvk/USER-bge-m3")
    
    names_file1 = extracted_text.splitlines()
    plan_original_text = best_plan_extracted.metadata.get("text_with_hours", "")
    names_file2 = plan_original_text.splitlines()

    clean_names_file1 = [extract_subject_name(line) for line in names_file1]
    clean_names_file2 = [extract_subject_name(line) for line in names_file2]

    embeddings_file1 = model.encode(clean_names_file1, convert_to_tensor=True)
    embeddings_file2 = model.encode(clean_names_file2, convert_to_tensor=True)
    used_indices = set()

    for idx, emb in enumerate(embeddings_file1):
        cosine_scores = util.cos_sim(emb, embeddings_file2)[0]

        cosine_scores = cosine_scores.detach().cpu().numpy()


        for used in used_indices:
            cosine_scores[used] = -np.inf


        best_idx = int(np.argmax(cosine_scores))
        best_score = float(cosine_scores[best_idx])
        used_indices.add(best_idx)


        hours1 = extract_hours(names_file1[idx])
        hours2 = extract_hours(names_file2[best_idx])
        hours_diff = None
        if hours1 is not None and hours2 is not None:
            hours_diff = abs(hours1 - hours2)

        logger.info(f"Предмет из учебной карточки: {names_file1[idx]}")
        logger.info(f"Предмет из учебного плана: {names_file2[best_idx]}, Схожесть: {best_score:.2f}")
        logger.info(f"Разница учебных часов: {hours_diff}")
        output_lines.append(f"Предмет из учебной карточки: {names_file1[idx]}")
        output_lines.append(f"Предмет из учебного плана: {names_file2[best_idx]}, Схожесть: {best_score:.2f}")
        output_lines.append(f"Разница учебных часов: {hours_diff}")
        
    return "\n".join(output_lines)
