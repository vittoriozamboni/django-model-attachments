import mimetypes
import json
import os

from django.conf import settings as dj_settings
from django.http import HttpResponse


"""
Attachments
"""

def handle_uploaded_file(uploadedfile, file_path):
    try:
        with open(file_path, 'wb+') as destination:
            for chunk in uploadedfile.chunks():
                destination.write(chunk)
    except Exception as e:
        raise(e)


class FileUploadReceiveResponse(HttpResponse):

    def __init__(self, request, file_dict, *args, **kwargs):
        files = file_dict if isinstance(file_dict, list) else [file_dict]
        data = json.dumps({'files': files})
        j = "application/json"
        accept = request.META.get('HTTP_ACCEPT')
        mime = j if accept and j in accept else 'text/plain'

        super(FileUploadReceiveResponse, self).__init__(data, mime, *args, **kwargs)


class FileUploadReceiveMixin(object):

    def receive_response(self, file_dict):
        return FileUploadReceiveResponse(self.request, file_dict)

    def receive(self, uploaded_file, **kwargs):
        overwrite_file = kwargs.get('overwrite_file', False)
        upload_root = kwargs.get('media_root', dj_settings.MEDIA_ROOT)
        destination_path = self.request.POST.get('destination_path', 'attachments')
        full_path = os.path.join(upload_root, destination_path)
        # This function should be called with user permissions
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        file_path = os.path.join(destination_path, uploaded_file.name)
        full_path = os.path.join(full_path, uploaded_file.name)
        if not os.path.exists(full_path) or overwrite_file:
            handle_uploaded_file(uploaded_file, full_path)
        file_dict = {
            'name': uploaded_file.name,
            'size': uploaded_file.size,
            'file_path': file_path,
        }
        return file_dict


class AttachmentFileUploadReceiveMixin(FileUploadReceiveMixin):

    def create_attached_files(self, sender_object, AttachmentModel, files_dict, model_field, **kwargs):
        extra_attributes = kwargs.get('extra_attributes', {})
        attachments = []
        for file_dict in files_dict:
            attachment = AttachmentModel(
                name=file_dict['name'],
                path=file_dict['file_path'],
                file_size=file_dict['size'],
                file_type=mimetypes.guess_type(file_dict['file_path'])[0]
            )
            attachment.audit_user = self.request.user
            if extra_attributes:
                for attribute_name, attribute_value in extra_attributes.iteritems():
                    setattr(attachment, attribute_name, attribute_value)
            attachment.save()
            attachments.append(attachment)
            getattr(sender_object, model_field).add(attachment)
        return attachments

    def process_uploaded_file(self, file_dict):
        """
        This must be re-defined in object's related view,
        in order to call self.create_attached_file with right properties
        i.e.:
        self.create_attached_file(post_instance, Attachment, file_dict, 'attachments',
                                  extra_attributes={'category': category_instance})
        """
        pass

    def return_response(self, files_dict):
        return self.receive_response(files_dict)
