tsuru app-create digitalmarketplace-admin-frontend python
tsuru env-set \
DM_ADMIN_FRONTEND_COOKIE_SECRET=secret \
DM_ADMIN_FRONTEND_PASSWORD_HASH=JHA1azIkMjcxMCRiNWZmMjhmMmExYTM0OGMyYTY0MjA3ZWFkOTIwNGM3NiQ4OGRLTHBUTWJQUE95UEVvSmg3djZYY2tWQ3lpcTZtaw== \
DM_DATA_API_AUTH_TOKEN=ourtoken \
DM_DATA_API_URL=https://digitalmarketplace-api-ci.tsuru.paas.alphagov.co.uk \
DM_S3_DOCUMENT_BUCKET=admin-frontend-dev-documents \
DM_SEARCH_API_AUTH_TOKEN=oursearchtoken \
DM_SEARCH_API_URL=https://digitalmarketplace-search-api-ci.tsuru.paas.alphagov.co.uk
tsuru app-deploy *
