import { useCallback, useEffect, useRef, useState } from "react";

const IDLE = { status: "idle", plan: null, result: null, error: null };

export default function useAgentRun(runAgent) {
  const [run, setRun] = useState(IDLE);
  const latest = useRef(IDLE);
  const controller = useRef(null);
  const runAgentRef = useRef(runAgent);
  runAgentRef.current = runAgent;

  const update = useCallback((next) => {
    latest.current = next;
    setRun(next);
  }, []);

  const start = useCallback(
    (plan) => {
      const { status } = latest.current;
      if (!runAgentRef.current || !plan) return;
      if (status === "running" || status === "awaiting_approval") return;

      controller.current?.abort();
      const current = new AbortController();
      controller.current = current;
      update({ status: "running", plan, result: null, error: null });

      runAgentRef.current(plan, { signal: current.signal }).then(
        (result) => {
          if (current.signal.aborted || controller.current !== current) return;
          controller.current = null;
          update({
            status: plan.risk === "R2" ? "awaiting_approval" : "done",
            plan,
            result,
            error: null,
          });
        },
        (error) => {
          if (current.signal.aborted || controller.current !== current) return;
          controller.current = null;
          update({ status: "error", plan, result: null, error });
        },
      );
    },
    [update],
  );

  const approve = useCallback(() => {
    if (latest.current.status !== "awaiting_approval") return;
    update({ ...latest.current, status: "done" });
  }, [update]);

  const reject = useCallback(() => {
    const { status } = latest.current;
    if (status !== "running" && status !== "awaiting_approval") return;
    controller.current?.abort();
    controller.current = null;
    update(IDLE);
  }, [update]);

  useEffect(
    () => () => {
      controller.current?.abort();
      controller.current = null;
    },
    [],
  );

  return { ...run, start, approve, reject };
}
