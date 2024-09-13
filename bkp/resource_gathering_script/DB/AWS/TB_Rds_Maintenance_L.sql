USE [MonitoringDB]
GO

/****** Object:  Table [dbo].[TB_Rds_Maintenance_L]    Script Date: 2022-02-11 ¿ÀÀü 9:35:09 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[TB_Rds_Maintenance_L](
	[CollectDTM] [datetime] NOT NULL,
	[ResourceIdentifier] [varchar](200) NOT NULL,
	[Summary] [varchar](100) NOT NULL,
	[Detail] [varchar](100) NOT NULL,
	[AutoAppliedAfterDate] [datetime] NULL,
	[ForcedApplyDate] [datetime] NULL,
	[CurrentApplyDate] [datetime] NULL,
	[RGPR_ID] [varchar](30) NULL,
	[RGST_DTM] [datetime] NULL,
	[MDFPR_ID] [varchar](30) NULL,
	[MDF_DTM] [datetime] NULL,
	[NOTE] [varchar](100) NULL,
 CONSTRAINT [PK_Rds_Maintenance_L] PRIMARY KEY CLUSTERED 
(
	[CollectDTM] DESC,
	[ResourceIdentifier] ASC,
	[Summary] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO


