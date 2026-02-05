"""Google Drive and Google Workspace documents collection module."""
from datetime import datetime, timedelta
from typing import List, Dict
import logging
from google_auth import (
    get_drive_service,
    get_docs_service,
    get_sheets_service,
    get_slides_service
)

logger = logging.getLogger(__name__)


class DriveCollector:
    """Collects document data from Google Drive and Workspace apps."""

    def __init__(self):
        self.drive_service = get_drive_service()
        self.docs_service = get_docs_service()
        self.sheets_service = get_sheets_service()
        self.slides_service = get_slides_service()

    def get_documents(self, days_back: int = 7) -> Dict[str, List[Dict]]:
        """Fetch documents modified in the past N days.

        Args:
            days_back: Number of days to look back

        Returns:
            Dictionary categorized by document type
        """
        logger.info(f"Fetching documents modified in the past {days_back} days...")

        # Calculate date range
        start_date = datetime.now() - timedelta(days=days_back)
        time_filter = start_date.strftime('%Y-%m-%dT%H:%M:%S')

        documents = {
            'docs': self._get_docs(time_filter),
            'sheets': self._get_sheets(time_filter),
            'slides': self._get_slides(time_filter),
            'other': self._get_other_files(time_filter)
        }

        logger.info(
            f"Found {len(documents['docs'])} docs, "
            f"{len(documents['sheets'])} sheets, "
            f"{len(documents['slides'])} slides, "
            f"{len(documents['other'])} other files"
        )

        return documents

    def _get_docs(self, modified_after: str) -> List[Dict]:
        """Get Google Docs modified after a specific time."""
        return self._get_files_by_mime_type(
            'application/vnd.google-apps.document',
            modified_after
        )

    def _get_sheets(self, modified_after: str) -> List[Dict]:
        """Get Google Sheets modified after a specific time."""
        return self._get_files_by_mime_type(
            'application/vnd.google-apps.spreadsheet',
            modified_after
        )

    def _get_slides(self, modified_after: str) -> List[Dict]:
        """Get Google Slides modified after a specific time."""
        return self._get_files_by_mime_type(
            'application/vnd.google-apps.presentation',
            modified_after
        )

    def _get_other_files(self, modified_after: str) -> List[Dict]:
        """Get other relevant files (PDFs, Office docs, etc.)."""
        mime_types = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        ]

        all_files = []
        for mime_type in mime_types:
            files = self._get_files_by_mime_type(mime_type, modified_after)
            all_files.extend(files)

        return all_files

    def _get_files_by_mime_type(
        self,
        mime_type: str,
        modified_after: str,
        max_results: int = 100
    ) -> List[Dict]:
        """Get files of a specific MIME type modified after a date.

        Args:
            mime_type: MIME type to filter by
            modified_after: ISO timestamp for modification filter
            max_results: Maximum number of results

        Returns:
            List of file dictionaries
        """
        try:
            query = (
                f"mimeType='{mime_type}' and "
                f"modifiedTime > '{modified_after}' and "
                f"trashed=false"
            )

            results = self.drive_service.files().list(
                q=query,
                pageSize=max_results,
                fields="files(id, name, mimeType, modifiedTime, "
                       "createdTime, owners, webViewLink, size, "
                       "lastModifyingUser, shared, permissions)"
            ).execute()

            files = results.get('files', [])
            parsed_files = []

            for file in files:
                parsed_file = self._parse_file(file)
                if parsed_file:
                    parsed_files.append(parsed_file)

            return parsed_files

        except Exception as e:
            logger.error(f"Error fetching files with mime type {mime_type}: {e}")
            return []

    def _parse_file(self, file: Dict) -> Dict:
        """Parse a file into a simplified format.

        Args:
            file: Raw file data from Google Drive API

        Returns:
            Parsed file dictionary
        """
        try:
            owners = file.get('owners', [])
            owner_email = owners[0].get('emailAddress', '') if owners else ''

            last_modifier = file.get('lastModifyingUser', {})
            modifier_email = last_modifier.get('emailAddress', '')

            return {
                'id': file.get('id', ''),
                'name': file.get('name', ''),
                'mime_type': file.get('mimeType', ''),
                'created_time': file.get('createdTime', ''),
                'modified_time': file.get('modifiedTime', ''),
                'owner': owner_email,
                'last_modifier': modifier_email,
                'web_link': file.get('webViewLink', ''),
                'size': file.get('size', '0'),
                'is_shared': file.get('shared', False),
                'permission_count': len(file.get('permissions', []))
            }

        except Exception as e:
            logger.warning(f"Error parsing file: {e}")
            return None

    def get_document_content(self, doc_id: str, doc_type: str) -> str:
        """Get the content of a document.

        Args:
            doc_id: Document ID
            doc_type: Type of document (docs, sheets, slides)

        Returns:
            Document content as text
        """
        try:
            if doc_type == 'docs':
                return self._get_doc_content(doc_id)
            elif doc_type == 'sheets':
                return self._get_sheet_content(doc_id)
            elif doc_type == 'slides':
                return self._get_slides_content(doc_id)
            else:
                return ""

        except Exception as e:
            logger.warning(f"Error getting content for {doc_id}: {e}")
            return ""

    def _get_doc_content(self, doc_id: str) -> str:
        """Get Google Doc content."""
        try:
            doc = self.docs_service.documents().get(documentId=doc_id).execute()
            content = doc.get('body', {}).get('content', [])

            text = []
            for element in content:
                if 'paragraph' in element:
                    para_elements = element['paragraph'].get('elements', [])
                    for para_element in para_elements:
                        text_run = para_element.get('textRun', {})
                        if 'content' in text_run:
                            text.append(text_run['content'])

            return ''.join(text)[:2000]  # Limit content length

        except Exception as e:
            logger.warning(f"Error getting doc content: {e}")
            return ""

    def _get_sheet_content(self, sheet_id: str) -> str:
        """Get Google Sheet content summary."""
        try:
            sheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()

            sheets = sheet.get('sheets', [])
            sheet_names = [s.get('properties', {}).get('title', '') for s in sheets]

            return f"Spreadsheet with {len(sheets)} sheets: {', '.join(sheet_names)}"

        except Exception as e:
            logger.warning(f"Error getting sheet content: {e}")
            return ""

    def _get_slides_content(self, slides_id: str) -> str:
        """Get Google Slides content summary."""
        try:
            presentation = self.slides_service.presentations().get(
                presentationId=slides_id
            ).execute()

            slides = presentation.get('slides', [])
            title = presentation.get('title', 'Untitled')

            return f"Presentation '{title}' with {len(slides)} slides"

        except Exception as e:
            logger.warning(f"Error getting slides content: {e}")
            return ""

    def get_documents_summary(self, days_back: int = 7) -> Dict:
        """Get a summary of document activity.

        Args:
            days_back: Number of days to look back

        Returns:
            Dictionary with document statistics and details
        """
        documents = self.get_documents(days_back)

        total_docs = (
            len(documents['docs']) +
            len(documents['sheets']) +
            len(documents['slides']) +
            len(documents['other'])
        )

        # Get documents created vs modified
        all_docs = (
            documents['docs'] +
            documents['sheets'] +
            documents['slides'] +
            documents['other']
        )

        created_count = sum(
            1 for doc in all_docs
            if self._is_recently_created(doc, days_back)
        )

        modified_count = total_docs - created_count

        return {
            'total_documents': total_docs,
            'docs_count': len(documents['docs']),
            'sheets_count': len(documents['sheets']),
            'slides_count': len(documents['slides']),
            'other_count': len(documents['other']),
            'created_count': created_count,
            'modified_count': modified_count,
            'documents': documents,
            'top_collaborators': self._get_top_collaborators(all_docs)
        }

    def _is_recently_created(self, doc: Dict, days_back: int) -> bool:
        """Check if a document was created within the lookback period."""
        try:
            created_time = datetime.fromisoformat(
                doc['created_time'].replace('Z', '+00:00')
            )
            cutoff_time = datetime.now(created_time.tzinfo) - timedelta(days=days_back)
            return created_time >= cutoff_time
        except Exception:
            return False

    def _get_top_collaborators(self, documents: List[Dict], limit: int = 10) -> List[Dict]:
        """Get most frequent collaborators.

        Args:
            documents: List of document dictionaries
            limit: Maximum number of collaborators to return

        Returns:
            List of top collaborators with counts
        """
        collaborator_count = {}

        for doc in documents:
            last_modifier = doc.get('last_modifier', '')
            if last_modifier:
                collaborator_count[last_modifier] = \
                    collaborator_count.get(last_modifier, 0) + 1

        sorted_collaborators = sorted(
            collaborator_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        return [
            {'email': email, 'edit_count': count}
            for email, count in sorted_collaborators
        ]
