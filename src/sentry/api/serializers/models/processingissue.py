from __future__ import absolute_import

import six

from sentry.api.serializers import register, Serializer
from sentry.models import ProcessingIssue


@register(ProcessingIssue)
class ProcessingIssueSerializer(Serializer):
    def get_attrs(self, item_list, user):
        counts = dict((i.id, getattr(i, 'num_events', None))
                      for i in item_list)

        missing_counts = []
        for pk, events in six.iteritems(counts):
            if events is None:
                missing_counts.append(pk)

        if missing_counts:
            extra_counts = ProcessingIssue.objects.with_num_events().filter(
                pk__in=list(missing_counts)).values('id', 'num_events')
            for d in extra_counts:
                counts[d['id']] = d['num_events']

        result = {}
        for item in item_list:
            result[item] = {
                'num_events': counts.get(item.id) or 0,
            }

        return result

    def serialize(self, obj, attrs, user):
        return {
            'id': six.text_type(obj.id),
            'type': obj.type,
            'checksum': obj.checksum,
            'numEvents': attrs['num_events'],
            'data': obj.data,
            'lastSeen': obj.datetime,
        }
