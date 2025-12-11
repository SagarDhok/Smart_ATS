from django import template

register = template.Library()

@register.filter
def score_color(score):
    try:
        score = float(score)
    except (ValueError, TypeError):
        return "badge-neutral"

    if score >= 90:
        return "badge-excellent"   
    elif score >= 80:
        return "badge-success"     
    elif score >= 65:
        return "badge-good"        
    elif score >= 50:
        return "badge-warning"     
    elif score >= 35:
        return "badge-danger"     
    else:
        return "badge-critical"  
