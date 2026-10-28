# Frontend

The frontend is a static, responsive LaunchPad MRECW site:

- `index.html` contains the page structure and dialogs.
- `css/styles.css` contains the supplied visual design.
- `js/app.js` handles navigation, filtering, rendering, API requests, and saved startups.

Serve it through the backend with `python backend\server.py` from the project root. The JavaScript uses same-origin `/api` endpoints in local mode, so opening `index.html` directly as a local file will not enable publishing or applications.

Startup bookmarks are saved in the current browser using local storage and can be filtered with the **Saved** chip. They are browser-specific and are not synced between devices or accounts.

To enable Supabase mode, run `supabase/schema.sql` in your Supabase project's SQL Editor and set the project URL and public anon/publishable key in `js/supabase-config.js`. The browser uses Supabase Auth; startup and application data requests go through the Python API, which verifies access tokens and applies PostgreSQL roles so database RLS policies are enforced. Leave the Supabase settings blank to use local SQLite. Never use a Supabase service-role/secret key in the frontend.

The frontend and Python API must be served from the same origin because API requests use relative `/api` paths. GitHub Pages alone cannot host the Python API. See the root README and `supabase/README.md` for deployment and configuration details.
