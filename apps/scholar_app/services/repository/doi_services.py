"""
DOI assignment and metadata management services.
Handles DOI minting, metadata updates, and citation formatting for research outputs.
"""

import requests
import logging
import xml.etree.ElementTree as ET
from typing import Dict, Optional, Any
from django.utils import timezone
from django.core.exceptions import ValidationError

from ...models import Dataset, SearchIndex, RepositoryConnection
from .repository_services import RepositoryServiceFactory

logger = logging.getLogger(__name__)


class DOIServiceError(Exception):
    """Base exception for DOI service errors"""

    pass


class DOIMetadataError(DOIServiceError):
    """DOI metadata related errors"""

    pass


class DOIAssignmentError(DOIServiceError):
    """DOI assignment related errors"""

    pass


class DataCiteMetadataBuilder:
    """Builder for DataCite metadata XML"""

    def __init__(self):
        self.metadata = {}

    def build_dataset_metadata(self, dataset: Dataset) -> str:
        """Build DataCite metadata XML for a dataset"""

        # Create root element
        root = ET.Element("resource")
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.set("xmlns", "http://datacite.org/schema/kernel-4")
        root.set(
            "xsi:schemaLocation",
            "http://datacite.org/schema/kernel-4 http://schema.datacite.org/meta/kernel-4.4/metadata.xsd",
        )

        # Identifier (DOI)
        if dataset.repository_doi:
            identifier = ET.SubElement(root, "identifier")
            identifier.set("identifierType", "DOI")
            identifier.text = dataset.repository_doi.replace(
                "https://doi.org/", ""
            ).replace("doi:", "")

        # Creators
        creators = ET.SubElement(root, "creators")

        # Main creator (owner)
        creator = ET.SubElement(creators, "creator")
        creator_name = ET.SubElement(creator, "creatorName")
        creator_name.set("nameType", "Personal")
        creator_name.text = dataset.owner.get_full_name() or dataset.owner.username

        if hasattr(dataset.owner, "orcid_id") and dataset.owner.orcid_id:
            name_identifier = ET.SubElement(creator, "nameIdentifier")
            name_identifier.set("schemeURI", "https://orcid.org")
            name_identifier.set("nameIdentifierScheme", "ORCID")
            name_identifier.text = dataset.owner.orcid_id

        if hasattr(dataset.owner, "affiliation") and dataset.owner.affiliation:
            affiliation = ET.SubElement(creator, "affiliation")
            affiliation.text = dataset.owner.affiliation

        # Additional creators (collaborators)
        for collaborator in dataset.collaborators.all():
            creator = ET.SubElement(creators, "creator")
            creator_name = ET.SubElement(creator, "creatorName")
            creator_name.set("nameType", "Personal")
            creator_name.text = collaborator.get_full_name() or collaborator.username

            if hasattr(collaborator, "orcid_id") and collaborator.orcid_id:
                name_identifier = ET.SubElement(creator, "nameIdentifier")
                name_identifier.set("schemeURI", "https://orcid.org")
                name_identifier.set("nameIdentifierScheme", "ORCID")
                name_identifier.text = collaborator.orcid_id

            if hasattr(collaborator, "affiliation") and collaborator.affiliation:
                affiliation = ET.SubElement(creator, "affiliation")
                affiliation.text = collaborator.affiliation

        # Titles
        titles = ET.SubElement(root, "titles")
        title = ET.SubElement(titles, "title")
        title.text = dataset.title

        # Publisher
        publisher = ET.SubElement(root, "publisher")
        publisher.text = dataset.repository_connection.repository.name

        # Publication year
        publication_year = ET.SubElement(root, "publicationYear")
        if dataset.published_at:
            publication_year.text = str(dataset.published_at.year)
        else:
            publication_year.text = str(dataset.created_at.year)

        # Resource type
        resource_type = ET.SubElement(root, "resourceType")
        resource_type.set("resourceTypeGeneral", "Dataset")
        resource_type.text = dataset.get_dataset_type_display()

        # Subjects (keywords)
        if dataset.keywords:
            subjects = ET.SubElement(root, "subjects")
            for keyword in dataset.keywords.split(","):
                keyword = keyword.strip()
                if keyword:
                    subject = ET.SubElement(subjects, "subject")
                    subject.text = keyword

        # Descriptions
        descriptions = ET.SubElement(root, "descriptions")
        description = ET.SubElement(descriptions, "description")
        description.set("descriptionType", "Abstract")
        description.text = dataset.description

        # Dates
        dates = ET.SubElement(root, "dates")

        # Created date
        created_date = ET.SubElement(dates, "date")
        created_date.set("dateType", "Created")
        created_date.text = dataset.created_at.strftime("%Y-%m-%d")

        # Updated date
        if dataset.updated_at != dataset.created_at:
            updated_date = ET.SubElement(dates, "date")
            updated_date.set("dateType", "Updated")
            updated_date.text = dataset.updated_at.strftime("%Y-%m-%d")

        # Available date
        if dataset.published_at:
            available_date = ET.SubElement(dates, "date")
            available_date.set("dateType", "Available")
            available_date.text = dataset.published_at.strftime("%Y-%m-%d")

        # Language
        language = ET.SubElement(root, "language")
        language.text = "en"  # Default to English

        # Version
        version = ET.SubElement(root, "version")
        version.text = dataset.version

        # Rights
        if dataset.license:
            rights_list = ET.SubElement(root, "rightsList")
            rights = ET.SubElement(rights_list, "rights")
            rights.text = dataset.license

            # Add common license URIs
            license_uris = {
                "CC-BY-4.0": "https://creativecommons.org/licenses/by/4.0/",
                "CC-BY-SA-4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
                "CC-BY-NC-4.0": "https://creativecommons.org/licenses/by-nc/4.0/",
                "CC0-1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
                "MIT": "https://opensource.org/licenses/MIT",
                "Apache-2.0": "https://opensource.org/licenses/Apache-2.0",
            }

            if dataset.license in license_uris:
                rights.set("rightsURI", license_uris[dataset.license])

        # Related identifiers
        if dataset.related_papers.exists():
            related_identifiers = ET.SubElement(root, "relatedIdentifiers")

            for paper in dataset.related_papers.all():
                if paper.doi:
                    related_identifier = ET.SubElement(
                        related_identifiers, "relatedIdentifier"
                    )
                    related_identifier.set("relatedIdentifierType", "DOI")
                    related_identifier.set("relationType", "IsSupplementTo")
                    related_identifier.text = paper.doi

        # Formats
        if dataset.file_formats:
            formats = ET.SubElement(root, "formats")
            for file_format in dataset.file_formats:
                format_elem = ET.SubElement(formats, "format")
                format_elem.text = file_format

        # Size
        if dataset.total_size_bytes > 0:
            sizes = ET.SubElement(root, "sizes")
            size = ET.SubElement(sizes, "size")
            size.text = dataset.get_file_size_display()

        return ET.tostring(root, encoding="unicode")

    def build_paper_metadata(self, paper: SearchIndex) -> str:
        """Build DataCite metadata XML for a research paper"""

        # Create root element
        root = ET.Element("resource")
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.set("xmlns", "http://datacite.org/schema/kernel-4")
        root.set(
            "xsi:schemaLocation",
            "http://datacite.org/schema/kernel-4 http://schema.datacite.org/meta/kernel-4.4/metadata.xsd",
        )

        # Identifier (DOI)
        if paper.doi:
            identifier = ET.SubElement(root, "identifier")
            identifier.set("identifierType", "DOI")
            identifier.text = paper.doi.replace("https://doi.org/", "").replace(
                "doi:", ""
            )

        # Creators
        creators = ET.SubElement(root, "creators")

        # Get authors through AuthorPaper relationship
        author_papers = paper.authors.through.objects.filter(paper=paper).order_by(
            "author_order"
        )

        for author_paper in author_papers:
            creator = ET.SubElement(creators, "creator")
            creator_name = ET.SubElement(creator, "creatorName")
            creator_name.set("nameType", "Personal")
            creator_name.text = author_paper.author.full_name

            if author_paper.author.orcid:
                name_identifier = ET.SubElement(creator, "nameIdentifier")
                name_identifier.set("schemeURI", "https://orcid.org")
                name_identifier.set("nameIdentifierScheme", "ORCID")
                name_identifier.text = author_paper.author.orcid

            if author_paper.author.affiliation:
                affiliation = ET.SubElement(creator, "affiliation")
                affiliation.text = author_paper.author.affiliation

        # Titles
        titles = ET.SubElement(root, "titles")
        title = ET.SubElement(titles, "title")
        title.text = paper.title

        # Publisher
        publisher = ET.SubElement(root, "publisher")
        if paper.journal:
            publisher.text = paper.journal.name
        else:
            publisher.text = paper.get_source_display()

        # Publication year
        publication_year = ET.SubElement(root, "publicationYear")
        if paper.publication_date:
            publication_year.text = str(paper.publication_date.year)
        else:
            publication_year.text = str(paper.created_at.year)

        # Resource type
        resource_type = ET.SubElement(root, "resourceType")
        resource_type.set("resourceTypeGeneral", "Text")
        resource_type.text = paper.get_document_type_display()

        # Subjects (keywords)
        if paper.keywords:
            subjects = ET.SubElement(root, "subjects")
            for keyword in paper.keywords.split(","):
                keyword = keyword.strip()
                if keyword:
                    subject = ET.SubElement(subjects, "subject")
                    subject.text = keyword

        # Descriptions
        if paper.abstract:
            descriptions = ET.SubElement(root, "descriptions")
            description = ET.SubElement(descriptions, "description")
            description.set("descriptionType", "Abstract")
            description.text = paper.abstract

        # Dates
        dates = ET.SubElement(root, "dates")

        if paper.publication_date:
            pub_date = ET.SubElement(dates, "date")
            pub_date.set("dateType", "Issued")
            pub_date.text = paper.publication_date.strftime("%Y-%m-%d")

        # Language
        language = ET.SubElement(root, "language")
        language.text = "en"  # Default to English

        # Related identifiers
        related_identifiers = ET.SubElement(root, "relatedIdentifiers")

        if paper.pmid:
            related_identifier = ET.SubElement(related_identifiers, "relatedIdentifier")
            related_identifier.set("relatedIdentifierType", "PMID")
            related_identifier.set("relationType", "IsIdenticalTo")
            related_identifier.text = paper.pmid

        if paper.arxiv_id:
            related_identifier = ET.SubElement(related_identifiers, "relatedIdentifier")
            related_identifier.set("relatedIdentifierType", "arXiv")
            related_identifier.set("relationType", "IsIdenticalTo")
            related_identifier.text = paper.arxiv_id

        return ET.tostring(root, encoding="unicode")


class DOIManager:
    """Service for managing DOI operations"""

    def __init__(self, repository_connection: RepositoryConnection):
        self.connection = repository_connection
        self.repository = repository_connection.repository
        self.metadata_builder = DataCiteMetadataBuilder()

    def assign_doi_to_dataset(
        self, dataset: Dataset, publish: bool = False
    ) -> Optional[str]:
        """Assign a DOI to a dataset through the repository"""

        try:
            # Build metadata
            metadata_xml = self.metadata_builder.build_dataset_metadata(dataset)

            # Get repository service
            service = RepositoryServiceFactory.create_service(self.connection)

            # Create or update dataset in repository
            if dataset.repository_id:
                # Update existing dataset
                repo_data = service.update_dataset(
                    dataset.repository_id,
                    {
                        "title": dataset.title,
                        "description": dataset.description,
                        "metadata_xml": metadata_xml,
                    },
                )
            else:
                # Create new dataset
                repo_data = service.create_dataset(
                    {
                        "title": dataset.title,
                        "description": dataset.description,
                        "metadata_xml": metadata_xml,
                    }
                )
                dataset.repository_id = repo_data.get("id")
                dataset.repository_url = repo_data.get("url")

            # Get DOI from repository response
            doi = repo_data.get("doi") or repo_data.get("conceptdoi")

            if doi:
                dataset.repository_doi = doi
                dataset.save()

                logger.info(f"Assigned DOI {doi} to dataset {dataset.id}")

                # Publish if requested
                if publish and dataset.repository_id:
                    self.publish_dataset_doi(dataset)

                return doi
            else:
                raise DOIAssignmentError("No DOI returned from repository")

        except Exception as e:
            logger.error(f"Failed to assign DOI to dataset {dataset.id}: {e}")
            raise DOIAssignmentError(f"DOI assignment failed: {e}")

    def publish_dataset_doi(self, dataset: Dataset) -> bool:
        """Publish a dataset DOI to make it publicly available"""

        try:
            if not dataset.repository_id:
                raise DOIAssignmentError(
                    "Dataset must be uploaded to repository before publishing DOI"
                )

            # Get repository service
            service = RepositoryServiceFactory.create_service(self.connection)

            # Publish dataset
            result = service.publish_dataset(dataset.repository_id)

            # Update dataset status
            dataset.status = "published"
            dataset.published_at = timezone.now()
            dataset.repository_url = result.get("url", dataset.repository_url)
            dataset.repository_doi = result.get("doi", dataset.repository_doi)
            dataset.save()

            logger.info(
                f"Published DOI for dataset {dataset.id}: {dataset.repository_doi}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to publish DOI for dataset {dataset.id}: {e}")
            raise DOIAssignmentError(f"DOI publication failed: {e}")

    def update_dataset_metadata(self, dataset: Dataset) -> bool:
        """Update dataset metadata including DOI metadata"""

        try:
            if not dataset.repository_id:
                logger.warning(
                    f"Dataset {dataset.id} has no repository ID, cannot update metadata"
                )
                return False

            # Build updated metadata
            metadata_xml = self.metadata_builder.build_dataset_metadata(dataset)

            # Get repository service
            service = RepositoryServiceFactory.create_service(self.connection)

            # Update dataset
            service.update_dataset(
                dataset.repository_id,
                {
                    "title": dataset.title,
                    "description": dataset.description,
                    "metadata_xml": metadata_xml,
                },
            )

            dataset.last_synced = timezone.now()
            dataset.save()

            logger.info(f"Updated metadata for dataset {dataset.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update metadata for dataset {dataset.id}: {e}")
            raise DOIMetadataError(f"Metadata update failed: {e}")

    def validate_doi_metadata(self, dataset: Dataset) -> Dict[str, Any]:
        """Validate DOI metadata for a dataset"""

        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metadata_completeness": 0.0,
        }

        required_fields = [
            ("title", dataset.title),
            ("description", dataset.description),
            ("owner", dataset.owner),
            ("repository_connection", dataset.repository_connection),
        ]

        optional_fields = [
            ("keywords", dataset.keywords),
            ("license", dataset.license),
            ("version", dataset.version),
            ("collaborators", dataset.collaborators.exists()),
        ]

        # Check required fields
        missing_required = []
        for field_name, field_value in required_fields:
            if not field_value:
                missing_required.append(field_name)
                validation_results["errors"].append(
                    f"Missing required field: {field_name}"
                )

        if missing_required:
            validation_results["valid"] = False

        # Check optional fields for completeness
        filled_optional = sum(1 for _, field_value in optional_fields if field_value)
        validation_results["metadata_completeness"] = (
            len(required_fields) + filled_optional
        ) / (len(required_fields) + len(optional_fields))

        # Specific validations
        if dataset.title and len(dataset.title) < 10:
            validation_results["warnings"].append(
                "Title is very short (less than 10 characters)"
            )

        if dataset.description and len(dataset.description) < 50:
            validation_results["warnings"].append(
                "Description is very short (less than 50 characters)"
            )

        if not dataset.keywords:
            validation_results["warnings"].append(
                "No keywords provided - this helps with discoverability"
            )

        if not dataset.license:
            validation_results["warnings"].append(
                "No license specified - consider adding an open license"
            )

        if dataset.file_count == 0:
            validation_results["warnings"].append(
                "No files in dataset - add data files before publishing"
            )

        # Check ORCID IDs for authors
        if not hasattr(dataset.owner, "orcid_id") or not dataset.owner.orcid_id:
            validation_results["warnings"].append(
                "Owner has no ORCID ID - this improves author identification"
            )

        return validation_results


class CitationFormatter:
    """Service for formatting citations from DOI metadata"""

    def __init__(self):
        self.styles = {}
        self._load_citation_styles()

    def _load_citation_styles(self):
        """Load citation style templates"""

        self.styles = {
            "apa": {
                "dataset": "{authors} ({year}). {title} [Data set]. {publisher}. {doi}",
                "article": "{authors} ({year}). {title}. {journal}, {volume}({issue}), {pages}. {doi}",
            },
            "mla": {
                "dataset": '{authors}. "{title}." {publisher}, {year}, {doi}.',
                "article": '{authors}. "{title}." {journal}, vol. {volume}, no. {issue}, {year}, pp. {pages}. {doi}.',
            },
            "chicago": {
                "dataset": '{authors}. "{title}." {publisher}, {year}. {doi}.',
                "article": '{authors}. "{title}." {journal} {volume}, no. {issue} ({year}): {pages}. {doi}.',
            },
            "vancouver": {
                "dataset": "{authors}. {title} [dataset]. {publisher}; {year}. Available from: {doi}",
                "article": "{authors}. {title}. {journal}. {year};{volume}({issue}):{pages}. Available from: {doi}",
            },
        }

    def format_dataset_citation(self, dataset: Dataset, style: str = "apa") -> str:
        """Format a dataset citation"""

        if style not in self.styles:
            style = "apa"

        template = self.styles[style].get("dataset", self.styles["apa"]["dataset"])

        # Prepare authors
        authors = dataset.owner.get_full_name() or dataset.owner.username
        collaborators = dataset.collaborators.all()

        if collaborators.count() == 1:
            authors += f" & {collaborators.first().get_full_name() or collaborators.first().username}"
        elif collaborators.count() > 1:
            collab_names = [c.get_full_name() or c.username for c in collaborators]
            authors += f", {', '.join(collab_names[:-1])}, & {collab_names[-1]}"

        # Prepare data
        citation_data = {
            "authors": authors,
            "year": dataset.published_at.year
            if dataset.published_at
            else dataset.created_at.year,
            "title": dataset.title,
            "publisher": dataset.repository_connection.repository.name,
            "doi": dataset.repository_doi or dataset.repository_url,
            "version": dataset.version,
        }

        try:
            return template.format(**citation_data)
        except KeyError as e:
            logger.warning(f"Missing field in citation template: {e}")
            return f"{authors} ({citation_data['year']}). {dataset.title}. {citation_data['publisher']}."

    def format_paper_citation(self, paper: SearchIndex, style: str = "apa") -> str:
        """Format a paper citation"""

        if style not in self.styles:
            style = "apa"

        template = self.styles[style].get("article", self.styles["apa"]["article"])

        # Prepare authors
        author_papers = paper.authors.through.objects.filter(paper=paper).order_by(
            "author_order"
        )
        author_names = [ap.author.full_name for ap in author_papers]

        if len(author_names) == 1:
            authors = author_names[0]
        elif len(author_names) == 2:
            authors = f"{author_names[0]} & {author_names[1]}"
        elif len(author_names) > 2:
            authors = f"{', '.join(author_names[:-1])}, & {author_names[-1]}"
        else:
            authors = "Unknown Author"

        # Prepare data
        citation_data = {
            "authors": authors,
            "year": paper.publication_date.year
            if paper.publication_date
            else paper.created_at.year,
            "title": paper.title,
            "journal": paper.journal.name
            if paper.journal
            else paper.get_source_display(),
            "volume": "",  # Would need to extract from paper metadata
            "issue": "",  # Would need to extract from paper metadata
            "pages": "",  # Would need to extract from paper metadata
            "doi": f"https://doi.org/{paper.doi}" if paper.doi else paper.external_url,
        }

        try:
            return template.format(**citation_data)
        except KeyError as e:
            logger.warning(f"Missing field in citation template: {e}")
            return f"{authors} ({citation_data['year']}). {paper.title}. {citation_data['journal']}."


# Utility functions
def auto_assign_doi_on_publish(dataset: Dataset) -> Optional[str]:
    """Automatically assign DOI when dataset is published"""

    if dataset.repository_doi:
        logger.info(f"Dataset {dataset.id} already has DOI: {dataset.repository_doi}")
        return dataset.repository_doi

    if not dataset.repository_connection:
        logger.warning(f"Dataset {dataset.id} has no repository connection")
        return None

    try:
        doi_manager = DOIManager(dataset.repository_connection)
        doi = doi_manager.assign_doi_to_dataset(dataset, publish=True)

        logger.info(f"Auto-assigned DOI {doi} to dataset {dataset.id}")
        return doi

    except Exception as e:
        logger.error(f"Failed to auto-assign DOI to dataset {dataset.id}: {e}")
        return None


def validate_and_format_doi(doi_string: str) -> Optional[str]:
    """Validate and format a DOI string"""

    if not doi_string:
        return None

    # Remove common prefixes
    doi_string = doi_string.strip()
    doi_string = doi_string.replace("https://doi.org/", "")
    doi_string = doi_string.replace("http://doi.org/", "")
    doi_string = doi_string.replace("doi:", "")
    doi_string = doi_string.replace("DOI:", "")

    # Basic DOI format validation
    import re

    doi_pattern = r"^10\.\d{4,}\/[-._;()\/:a-zA-Z0-9]+$"

    if re.match(doi_pattern, doi_string):
        return doi_string
    else:
        raise ValidationError(f"Invalid DOI format: {doi_string}")


def get_doi_metadata(doi: str) -> Optional[Dict]:
    """Retrieve metadata for a DOI from CrossRef or DataCite"""

    try:
        # Try CrossRef first
        response = requests.get(
            f"https://api.crossref.org/works/{doi}",
            headers={"Accept": "application/json"},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            return {
                "source": "crossref",
                "title": data["message"].get("title", [""])[0],
                "authors": [
                    f"{author.get('given', '')} {author.get('family', '')}"
                    for author in data["message"].get("author", [])
                ],
                "publisher": data["message"].get("publisher"),
                "published_date": data["message"]
                .get("published-print", {})
                .get("date-parts", [[None]])[0][0],
                "type": data["message"].get("type"),
                "url": data["message"].get("URL"),
                "abstract": data["message"].get("abstract"),
            }

    except Exception as e:
        logger.warning(f"Failed to get metadata from CrossRef for DOI {doi}: {e}")

    try:
        # Try DataCite
        response = requests.get(
            f"https://api.datacite.org/dois/{doi}",
            headers={"Accept": "application/json"},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            attributes = data["data"]["attributes"]

            return {
                "source": "datacite",
                "title": attributes.get("titles", [{}])[0].get("title"),
                "authors": [
                    creator.get("name") for creator in attributes.get("creators", [])
                ],
                "publisher": attributes.get("publisher"),
                "published_date": attributes.get("published"),
                "type": attributes.get("resourceTypeGeneral"),
                "url": attributes.get("url"),
                "description": attributes.get("descriptions", [{}])[0].get(
                    "description"
                ),
            }

    except Exception as e:
        logger.warning(f"Failed to get metadata from DataCite for DOI {doi}: {e}")

    return None
