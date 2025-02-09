# myapp/templatetags/custom_tags.py
from django import template
from ..models import ProductionQueue

register = template.Library()

@register.filter
def filter_by_field(value, arg):
    return ProductionQueue.objects.filter(some_field=arg)


@register.filter
def filter_by_fields(values, arg):
    # arg should be a string formatted like "field1=value1,field2=value2"
    args = dict(item.split('=') for item in arg.split(','))

    # Start with the queryset
    queryset = values

    # Apply filters based on the provided arguments
    for key, value in args.items():
        vl = value.lower()
        if vl == 'none':
            # Handle None explicitly
            queryset = queryset.filter(**{f"{key}__isnull": True})
        elif vl == 'notnone':
            queryset = queryset.filter(**{f"{key}__isnull": False})
        else:
            # For non-None values, apply the filter normally
            queryset = queryset.filter(**{key: value})

    return queryset

    return queryset