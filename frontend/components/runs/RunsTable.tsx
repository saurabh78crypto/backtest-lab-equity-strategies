"use client";

import { Trash2 } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Table, Td, Th, Thead, Tr } from "@/components/ui/Table";
import { useDeleteRun } from "@/hooks/useDeleteRun";
import { formatDateTime } from "@/lib/format";
import type { BacktestRunSummary } from "@/lib/types";

export function RunsTable({ runs }: { runs: BacktestRunSummary[] }) {
  const deleteRun = useDeleteRun();
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);

  function handleDelete(id: string) {
    if (pendingDeleteId !== id) {
      setPendingDeleteId(id);
      return;
    }
    deleteRun.mutate(id, { onSettled: () => setPendingDeleteId(null) });
  }

  return (
    <Table>
      <Thead>
        <tr>
          <Th>Name</Th>
          <Th>Status</Th>
          <Th>Created</Th>
          <Th align="right">Actions</Th>
        </tr>
      </Thead>
      <tbody>
        {runs.map((run) => (
          <Tr key={run.id}>
            <Td>
              <Link href={`/runs/${run.id}`} className="font-medium text-ink-primary hover:text-accent">
                {run.name}
              </Link>
              {run.status === "failed" && run.error_message && (
                <p className="mt-0.5 max-w-md truncate text-2xs text-negative" title={run.error_message}>
                  {run.error_message}
                </p>
              )}
            </Td>
            <Td>
              <StatusBadge status={run.status} />
            </Td>
            <Td className="font-mono text-ink-secondary">{formatDateTime(run.created_at)}</Td>
            <Td align="right">
              <div className="flex justify-end gap-2">
                <Link href={`/runs/${run.id}`}>
                  <Button variant="secondary" size="sm">
                    View
                  </Button>
                </Link>
                <Button
                  variant="danger"
                  size="sm"
                  loading={deleteRun.isPending && pendingDeleteId === run.id}
                  onClick={() => handleDelete(run.id)}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                  {pendingDeleteId === run.id ? "Confirm?" : ""}
                </Button>
              </div>
            </Td>
          </Tr>
        ))}
      </tbody>
    </Table>
  );
}
