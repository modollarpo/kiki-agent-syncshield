import React, { useEffect, useState } from 'react';
import { Modal, Table, Button, Loader, Avatar } from '@kiki/ui';
import { fetchTeamMembers, addTeamMember, removeTeamMember, updateTeamMemberRole } from '../utils/api';
import { UserRole } from '../types/roles';

interface TeamMembersModalProps {
  teamId: string;
  open: boolean;
  onClose: () => void;
}

interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatarUrl?: string;
}

const roleLabels: Record<UserRole, string> = {
  admin: 'Admin',
  owner: 'Owner',
  manager: 'Manager',
  member: 'Member',
  viewer: 'Viewer',
};

const TeamMembersModal: React.FC<TeamMembersModalProps> = ({ teamId, open, onClose }) => {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [addEmail, setAddEmail] = useState('');
  const [addRole, setAddRole] = useState<UserRole>('member');
  const [addLoading, setAddLoading] = useState(false);
  const [addError, setAddError] = useState<string | null>(null);
  const [removingId, setRemovingId] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const fetchMembers = () => {
    setLoading(true);
    fetchTeamMembers(teamId)
      .then(setMembers)
      .catch(() => setError('Failed to load team members.'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (open) fetchMembers();
    // eslint-disable-next-line
  }, [open, teamId]);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    setAddLoading(true);
    setAddError(null);
    try {
      await addTeamMember(teamId, addEmail, addRole);
      setAddEmail('');
      setAddRole('member');
      fetchMembers();
    } catch (err: any) {
      setAddError(err?.response?.data?.message || 'Failed to add member.');
    } finally {
      setAddLoading(false);
    }
  };

  const handleRemove = async (userId: string) => {
    setRemovingId(userId);
    try {
      await removeTeamMember(teamId, userId);
      setMembers(members => members.filter(m => m.id !== userId));
    } catch {
      setError('Failed to remove member.');
    } finally {
      setRemovingId(null);
    }
  };

  const handleRoleChange = async (userId: string, role: UserRole) => {
    setUpdatingId(userId);
    try {
      await updateTeamMemberRole(teamId, userId, role);
      setMembers(members => members.map(m => m.id === userId ? { ...m, role } : m));
    } catch {
      setError('Failed to update role.');
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title="Team Members">
      <div className="p-4">
        <form className="flex gap-2 mb-4" onSubmit={handleAdd}>
          <input
            type="email"
            placeholder="User email"
            className="px-2 py-1 rounded bg-gray-900 border border-gray-700 text-gray-100"
            value={addEmail}
            onChange={e => setAddEmail(e.target.value)}
            required
          />
          <select
            className="px-2 py-1 rounded bg-gray-900 border border-gray-700 text-gray-100"
            value={addRole}
            onChange={e => setAddRole(e.target.value as UserRole)}
          >
            {Object.entries(roleLabels).map(([role, label]) => (
              <option key={role} value={role}>{label}</option>
            ))}
          </select>
          <Button type="submit" variant="primary" loading={addLoading}>Add</Button>
        </form>
        {addError && <div className="text-red-500 text-sm mb-2">{addError}</div>}
        <Table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {members.map(member => (
              <tr key={member.id}>
                <td className="flex items-center gap-2"><Avatar name={member.name} size="sm" />{member.name}</td>
                <td>{member.email}</td>
                <td>
                  <select
                    className="px-2 py-1 rounded bg-gray-900 border border-gray-700 text-gray-100"
                    value={member.role}
                    onChange={e => handleRoleChange(member.id, e.target.value as UserRole)}
                    disabled={updatingId === member.id}
                  >
                    {Object.entries(roleLabels).map(([role, label]) => (
                      <option key={role} value={role}>{label}</option>
                    ))}
                  </select>
                </td>
                <td>
                  <Button size="sm" variant="danger" onClick={() => handleRemove(member.id)} disabled={removingId === member.id}>
                    {removingId === member.id ? <Loader size="xs" /> : 'Remove'}
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
        {loading && <div className="mt-4"><Loader /></div>}
        {error && <div className="text-red-500 text-sm mt-2">{error}</div>}
      </div>
    </Modal>
  );
};

export default TeamMembersModal;
