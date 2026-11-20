import { useCallback, useEffect, useRef, useState } from "react";

const IDLE = { status: "idle", plan: null, result: null, error: null };

export default function useAgentRun(runAgent) {
  const [state, setState] = useState(IDLE);
  const stateRef = useRef(state);
  const controllerRef = useRef(null);
  const runAgentRef = useRef(runAgent);
  runAgentRef.current = runAgent;

  const update = useCallback((next) => {
    stateRef.current = next;
    setState(next);
  }, []);

  const start = useCallback(
    (plan) => {
      const current = stateRef.current;
      if (!runAgentRef.current || !plan) return;
      if (current.status === "running" || current.status === "awaiting_approval") return;

      controllerRef.current?.abort();
      const controller = new AbortController();
      controllerRef.current = controller;
      update({ status: "running", plan, result: null, error: null });

      let promise;
      try {
        promise = runAgentRef.current(plan, { signal: controller.signal });
      } catch (error) {
        if (controllerRef.current === controller) {
          controllerRef.current = null;
          update({ status: "error", plan, result: null, error });
        }
        return;
      }

      Promise.resolve(promise).then(
        (result) => {
          if (controllerRef.current !== controller || controller.signal.aborted) return;
          controllerRef.current = null;
          update({
            status: plan.risk === "R2" ? "awaiting_approval" : "done",
            plan,
            result,
            error: null,
          });
        },
        (error) => {
          if (controllerRef.current !== controller || controller.signal.aborted) return;
          controllerRef.current = null;
          update({ status: "error", plan, result: null, error });
        },
      );
    },
    [update],
  );

  const approve = useCallback(() => {
    const current = stateRef.current;
    if (current.status !== "awaiting_approval") return;
    update({ ...current, status: "done" });
  }, [update]);

  const reject = useCallback(() => {
    const current = stateRef.current;
    if (current.status !== "running" && current.status !== "awaiting_approval") return;
    controllerRef.current?.abort();
    controllerRef.current = null;
    update(IDLE);
  }, [update]);

  useEffect(
    () => () => {
      controllerRef.current?.abort();
      controllerRef.current = null;
    },
    [],
  );

  return { ...state, start, approve, reject };
}
