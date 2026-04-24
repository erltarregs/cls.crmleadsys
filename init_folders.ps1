$folders = @(
    "app\core",
    "app\db",
    "app\models",
    "app\schemas",
    "app\crud",
    "app\api\routes",
    "app\services",
    "alembic",
    "tests",
    "uploads\photos"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Force -Path $folder
}
