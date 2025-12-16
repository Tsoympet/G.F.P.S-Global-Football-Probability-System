import { api } from '@api/client';
import { DataTable } from '@components/DataTable';
import { useQuery } from '@hooks/useQuery';
import { palette } from '@theme/palette';
import { ModelInfo } from '@api/types';

export const ModelsTraining = () => {
  const models = useQuery(api.models, []);

  const handleTrain = async () => {
    try {
      await api.trainModel();
    } catch (error) {
      console.error(error);
    }
  };

  const handleActivate = async (version: string) => {
    try {
      await api.activateModel(version);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <section
      style={{
        border: `1px solid ${palette.border}`,
        borderRadius: 14,
        background: palette.cardElevated,
        padding: 16,
        display: 'flex',
        flexDirection: 'column',
        gap: 12
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ color: palette.textPrimary, fontSize: 20, fontWeight: 700 }}>Models & Training</div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            onClick={handleTrain}
            style={{
              background: 'linear-gradient(90deg, #1f9ae5, #0fd7a1)',
              color: '#0b0f1a',
              border: 'none',
              padding: '10px 14px',
              borderRadius: 10,
              fontWeight: 700,
              cursor: 'pointer'
            }}
          >
            Train new model
          </button>
        </div>
      </div>
      <DataTable<ModelInfo>
        columns={[
          { header: 'Version', key: 'version' },
          { header: 'ROI', key: 'roi', render: (row) => `${(row.roi * 100).toFixed(2)}%` },
          { header: 'LogLoss', key: 'logLoss', render: (row) => row.logLoss.toFixed(3) },
          {
            header: 'Status',
            key: 'status',
            render: (row) => (
              <span style={{ color: row.status === 'active' ? '#22c55e' : palette.textSecondary }}>{row.status}</span>
            )
          },
          {
            header: 'Actions',
            key: 'version',
            render: (row) => (
              <button
                onClick={() => handleActivate(row.version)}
                style={{
                  background: 'transparent',
                  border: `1px solid ${palette.border}`,
                  color: palette.textPrimary,
                  padding: '8px 12px',
                  borderRadius: 10,
                  cursor: 'pointer'
                }}
              >
                Activate
              </button>
            )
          }
        ]}
        data={models.data ?? []}
      />
    </section>
  );
};
