# Frontend entrypoint - set up env and start dev server

# Use provided VITE_API_URL or default
export VITE_API_URL="${VITE_API_URL:-http://192.168.2.186:8000/api/v1}"

echo "Starting Vite dev server..."
echo "API URL: $VITE_API_URL"

# Start npm dev
exec npm run dev
