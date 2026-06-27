from django.core.exceptions import ValidationError


def validate_review_topics(semester_subject, topics):
    """
    Checks that all topics selected for a DailyClassReview belong to the catalog of the semester subject.
    """
    subject_catalog = semester_subject.subject_catalog
    for topic in topics:
        if topic.subject_unit.subject_catalog != subject_catalog:
            raise ValidationError(f"Topic '{topic.title}' does not belong to subject catalog '{subject_catalog.name}'")
