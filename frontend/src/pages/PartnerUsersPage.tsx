import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useRef } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiError, createPartnerUser, getPartner, getPartnerUsers, getRegistrationOptions, updatePartnerUser } from "../api/client";
import { useAuth } from "../features/auth/AuthContext";

export function PartnerUsersPage() {
  const { partnerId = "" } = useParams();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const formRef = useRef<HTMLFormElement>(null);
  const partner = useQuery({ queryKey: ["partner", partnerId], queryFn: () => getPartner(partnerId) });
  const users = useQuery({ queryKey: ["partner-users", partnerId], queryFn: () => getPartnerUsers(partnerId) });
  const options = useQuery({ queryKey: ["registration-options"], queryFn: getRegistrationOptions });
  const canManage = user?.is_superuser || user?.roles.includes("TCG_ADMIN") || user?.roles.includes("PARTNER_ADMIN");
  const createUser = useMutation({
    mutationFn: (body: Record<string, unknown>) => createPartnerUser(partnerId, body),
    onSuccess: () => {
      formRef.current?.reset();
      return queryClient.invalidateQueries({ queryKey: ["partner-users", partnerId] });
    },
  });
  const updateUser = useMutation({ mutationFn: ({ id, isActive }: { id: string; isActive: boolean }) => updatePartnerUser(partnerId, id, { is_active: isActive }), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["partner-users", partnerId] }) });
  const updateRole = useMutation({ mutationFn: ({ id, role }: { id: string; role: string }) => updatePartnerUser(partnerId, id, { role_codes: [role] }), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["partner-users", partnerId] }) });

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    createUser.mutate({ email: form.get("email"), full_name: form.get("full_name"), password: form.get("password"), role_codes: [form.get("role_code")] });
  }

  const error = createUser.error instanceof ApiError ? createUser.error.message : null;
  return <div className="workspace-page">
    <header className="page-heading"><div><Link className="back-link" to={`/partners/${partnerId}`}>← {partner.data?.company_name ?? "Partner"}</Link><span className="eyebrow">Access management</span><h1>Partner users</h1><p>Control who can access this partner workspace and what they can do.</p></div></header>
    <div className="users-layout">
      <section className="content-card table-card"><div className="card-heading"><h2>Team members</h2><span>{users.data?.length ?? 0}</span></div>
        {users.isLoading && <p className="notice">Loading users…</p>}
        {users.data?.map((member) => <div className="user-row" key={member.id}><span className="avatar">{member.full_name.charAt(0)}</span><span><strong>{member.full_name}</strong><small>{member.email}</small></span>{canManage ? <select className="role-select" aria-label={`Role for ${member.full_name}`} value={member.roles[0]} onChange={(event) => updateRole.mutate({ id: member.id, role: event.target.value })}>{options.data?.partner_roles.map((role) => <option value={role.code} key={role.id}>{role.name}</option>)}</select> : <span className="user-role">{member.roles.map((role) => role.replace("PARTNER_", "").replaceAll("_", " ")).join(", ")}</span>}{canManage && member.id !== user?.id ? <button className="row-action" type="button" onClick={() => updateUser.mutate({ id: member.id, isActive: !member.is_active })}>{member.is_active ? "Deactivate" : "Activate"}</button> : <span className={`status-dot ${member.is_active ? "status-dot--active" : ""}`} title={member.is_active ? "Active" : "Inactive"} />}</div>)}
      </section>
      {canManage && <form ref={formRef} className="content-card compact-form" onSubmit={submit}><span className="status-kicker">Add access</span><h2>New team member</h2>{error && <div className="form-alert form-alert--error">{error}</div>}
        <label>Full name<input name="full_name" required minLength={2} /></label><label>Email<input name="email" type="email" required /></label><label>Temporary password<input name="password" type="password" required minLength={12} /></label><label>Role<select name="role_code">{options.data?.partner_roles.map((role) => <option value={role.code} key={role.id}>{role.name}</option>)}</select></label><button type="submit" disabled={createUser.isPending}>{createUser.isPending ? "Adding…" : "Add user"}</button>
      </form>}
    </div>
  </div>;
}
