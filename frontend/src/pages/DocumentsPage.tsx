import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";

import { ApiError, downloadDocument, getDocuments, uploadDocument } from "../api/client";
import { useAuth } from "../features/auth/AuthContext";

export function DocumentsPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const canPublish = Boolean(user?.is_superuser || user?.roles.includes("TCG_ADMIN"));
  const documents = useQuery({ queryKey: ["documents", search], queryFn: () => getDocuments(search ? `search=${encodeURIComponent(search)}` : "") });
  const upload = useMutation({
    mutationFn: uploadDocument,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["documents"] }),
  });

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    upload.mutate(new FormData(event.currentTarget));
    event.currentTarget.reset();
  }

  async function download(id: string) {
    const result = await downloadDocument(id);
    window.location.assign(result.url);
  }

  const error = upload.error instanceof ApiError ? upload.error.message : null;
  return <div className="workspace-page">
    <header className="page-heading"><span className="eyebrow">Private repository</span><h1>Documents</h1><p>Versioned sales, product, pricing, proposal, and delivery content with partner-aware access.</p></header>
    <div className="catalog-layout">
      <section className="content-card table-card">
        <div className="table-toolbar"><input className="search-field" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search title or description" /></div>
        <div className="table-scroll"><table><thead><tr><th>Document</th><th>Category</th><th>Audience</th><th>Version</th><th /></tr></thead><tbody>
          {documents.data?.map((document) => {
            const latest = [...document.versions].sort((a, b) => b.version_number - a.version_number)[0];
            return <tr key={document.id}><td><strong>{document.title}</strong><small>{document.description ?? latest?.file_name}</small></td><td>{document.category.replaceAll("_", " ")}</td><td><span className="status-pill">{document.visibility.replaceAll("_", " ")}</span></td><td>{latest ? `v${latest.version_number}` : "—"}</td><td><button className="row-action" type="button" onClick={() => void download(document.id)}>Download</button></td></tr>;
          })}
        </tbody></table></div>
        {!documents.isLoading && !documents.data?.length && <div className="empty-state"><h2>No documents found</h2><p>Published content will appear here.</p></div>}
      </section>
      {canPublish && <form className="content-card compact-form catalog-create" onSubmit={submit}>
        <span className="status-kicker">Publisher</span><h2>Publish document</h2>
        {error && <div className="form-alert form-alert--error">{error}</div>}
        <label>Title<input name="title" required /></label>
        <label>Category<select name="category" defaultValue="SALES_ENABLEMENT"><option value="SALES_ENABLEMENT">Sales Enablement</option><option value="PRODUCT_DOCUMENTATION">Product Documentation</option><option value="IMPLEMENTATION_GUIDE">Implementation Guide</option><option value="PRICING">Pricing</option><option value="PROPOSAL_TEMPLATE">Proposal Template</option><option value="SOW_TEMPLATE">SOW Template</option><option value="RFP">RFP</option><option value="OTHER">Other</option></select></label>
        <label>Audience<select name="visibility" defaultValue="ALL_PARTNERS"><option value="ALL_PARTNERS">All Partners</option><option value="TCG_INTERNAL">TCG Internal</option></select></label>
        <label>Description<textarea name="description" rows={3} /></label>
        <label>File<input name="file" type="file" required /></label>
        <button type="submit" disabled={upload.isPending}>Publish</button>
      </form>}
    </div>
  </div>;
}
